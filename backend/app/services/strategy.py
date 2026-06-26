import pandas as pd
import pandas_ta as ta
import threading
import logging
from datetime import datetime

# Modular Imports
from app.services.order_manager import OrderManager
from app.services.risk_manager import RiskManager
from app.db.session import SessionLocal
from app.db import models

logger = logging.getLogger("AlphaTrade")

class StrategyService:
    def __init__(self, api_obj, capital=10000):
        self.api = api_obj
        self.risk = RiskManager(total_capital=capital)
        self.order_manager = OrderManager(api_obj)
        
        # Internal State
        self.active_positions = {}
        self.indicator_cache = {} # {token: {'vwap': x, 'orb_high': y, 'minute': z}}
        self.history_cache = {}
        
        # Thread Safety
        self._lock = threading.Lock()
        
        # Sync memory with DB on boot
        self.sync_with_db()

    def sync_with_db(self):
        """Loads today's existing trades into memory so we don't double-buy"""
        db = SessionLocal()
        try:
            existing_trades = db.query(models.Trade).all()
            for t in existing_trades:
                self.active_positions[t.symbol] = {
                    'qty': t.qty,
                    'entry': t.entry_price,
                    'side': t.side
                }
                self.risk.current_trades += 1
            logger.info(f"📊 Strategy Memory Synced: {len(self.active_positions)} positions active.")
        finally:
            db.close()

    def check_for_signals(self, symbol, token, current_price):
        """
        EVENT-DRIVEN: Triggered by WebSocket for the 5 stocks YOU selected.
        """
        with self._lock:
            # 1. If we already bought this stock, check for Target/SL
            if symbol in self.active_positions:
                self._manage_exit_logic(symbol, token, current_price)
                return

            # 2. Capital Protection: Stop if we already took our 1 best trade for the day
            # (Adjust this limit in RiskManager if you want to trade more than 1 of the 5)
            if self.risk.current_trades >= self.risk.max_trades_per_day:
                return

            # 3. Calculate Indicators (ORB & VWAP) only for your selected stocks
            indicators = self._get_cached_indicators(symbol, token)
            if not indicators: 
                return

            orb_high = indicators['orb_high']
            vwap = indicators['vwap']

            # 4. EXECUTION LOGIC (The 'Best-of-5' Race)
            # We only buy if Price > 15m High AND Price > VWAP
            if current_price > orb_high and current_price > vwap:
                # Calculate how strong the breakout is
                strength = ((current_price - orb_high) / orb_high) * 100
                
                # Minimum threshold to confirm it's not a 'fake' breakout
                if strength > 0.15:
                    logger.info(f"🚀 BREAKOUT DETECTED: {symbol} is the winner! Strength: {strength:.2f}%")
                    
                    qty = self.risk.calculate_quantity(current_price)
                    res = self.order_manager.place_intraday_order(symbol, token, qty, "BUY")
                    
                    if res['status'] == "success":
                        self.active_positions[symbol] = {
                            'qty': qty, 
                            'entry': current_price,
                            'side': 'BUY'
                        }
                        self.risk.current_trades += 1

    def _get_cached_indicators(self, symbol, token):
        """Standard Indicator Calculation (ORB + VWAP)"""
        current_minute = datetime.now().minute
        
        if token in self.indicator_cache:
            if self.indicator_cache[token]['minute'] == current_minute:
                return self.indicator_cache[token]

        df = self._get_historical_data(token)
        if df is not None and not df.empty and len(df) >= 15:
            try:
                vwap_series = ta.vwap(high=df.high, low=df.low, close=df.close, volume=df.volume)
                # ORB High is the maximum price of the first 15 one-minute candles
                orb_high = df.iloc[:15]['high'].max()
                
                self.indicator_cache[token] = {
                    'vwap': vwap_series.iloc[-1],
                    'orb_high': orb_high,
                    'minute': current_minute
                }
                return self.indicator_cache[token]
            except Exception as e:
                logger.error(f"Math error for {symbol}: {e}")
        return None

    def _get_historical_data(self, symbol_token):
        """Internal helper to fetch candles with 45s cooldown"""
        now = datetime.now()
        if symbol_token in self.history_cache:
            if (now - self.history_cache[symbol_token]['ts']).total_seconds() < 45:
                return self.history_cache[symbol_token]['df']

        try:
            today = now.strftime("%Y-%m-%d")
            params = {
                "exchange": "NSE", "symboltoken": symbol_token, "interval": "ONE_MINUTE",
                "fromdate": f"{today} 09:15", "todate": f"{today} 15:30"
            }
            res = self.api.getCandleData(params)
            if res['status'] and res['data']:
                df = pd.DataFrame(res['data'], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                cols = ['open', 'high', 'low', 'close', 'volume']
                df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True).sort_index(inplace=True)
                self.history_cache[symbol_token] = {'df': df, 'ts': now}
                return df
        except: pass
        return None

    def _manage_exit_logic(self, symbol, token, ltp):
        """Profit Target: 1.5% | Stop Loss: 1.0%"""
        pos = self.active_positions[symbol]
        target = pos['entry'] * 1.015
        sl = pos['entry'] * 0.99

        if ltp >= target or ltp <= sl:
            logger.info(f"🎯 EXIT SIGNAL: {symbol} reached Target/SL. Closing.")
            res = self.order_manager.place_intraday_order(symbol, token, pos['qty'], "SELL")
            if res['status'] == "success":
                del self.active_positions[symbol]