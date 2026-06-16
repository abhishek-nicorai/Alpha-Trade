import pandas as pd
import pandas_ta as ta
from datetime import datetime, timedelta
import time as sleep_timer
from app.services.order_manager import OrderManager
from app.services.risk_manager import RiskManager

class StrategyService:
    def __init__(self, api_obj, capital=10000):
        self.api = api_obj
        self.opening_range = {}
        self.risk = RiskManager(total_capital=capital)
        self.order_manager = OrderManager(api_obj)
        self.active_positions = {}
        
        # NEW: Cache to prevent Rate Limiting
        self.history_cache = {} # {token: {'data': df, 'last_fetched': timestamp}}

    def get_historical_data(self, symbol_token, interval="ONE_MINUTE"):
        """Fetches candles with caching to avoid 'Access Denied' rate limits"""
        now = datetime.now()
        
        # Check cache: If we fetched this stock less than 50 seconds ago, reuse data
        if symbol_token in self.history_cache:
            last_time = self.history_cache[symbol_token]['last_fetched']
            if (now - last_time).total_seconds() < 50:
                return self.history_cache[symbol_token]['data']

        try:
            today = now.strftime("%Y-%m-%d")
            params = {
                "exchange": "NSE",
                "symboltoken": symbol_token,
                "interval": interval,
                "fromdate": f"{today} 09:15",
                "todate": f"{today} 15:30"
            }
            res = self.api.getCandleData(params)
            
            if res['status'] and res['data'] and len(res['data']) > 0:
                df = pd.DataFrame(res['data'], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
                cols = ['open', 'high', 'low', 'close', 'volume']
                df[cols] = df[cols].apply(pd.to_numeric, errors='coerce')
                
                # CRITICAL: Fix for "VWAP requires an ordered DatetimeIndex"
                df['timestamp'] = pd.to_datetime(df['timestamp'])
                df.set_index('timestamp', inplace=True)
                df.sort_index(inplace=True)
                
                # Update Cache
                self.history_cache[symbol_token] = {'data': df, 'last_fetched': now}
                return df
                
            return None
        except Exception as e:
            if "Access denied" in str(e):
                print(f"🚫 API Rate Limit Hit for {symbol_token}. Waiting...")
            return None

    def check_for_signals(self, symbol, token, current_price):
        if token in self.active_positions:
            self._manage_exit_logic(symbol, token, current_price)
            return

        can_trade, _ = self.risk.can_trade()
        if not can_trade: return

        # Get ORB High/Low
        range_data = self.opening_range.get(token) or self.calculate_orb(token)
        if not range_data: return

        # Get Data for VWAP
        df = self.get_historical_data(token)
        
        # FIX: Ensure df is not None before processing
        if df is not None and not df.empty and len(df) > 1:
            try:
                vwap_series = ta.vwap(high=df.high, low=df.low, close=df.close, volume=df.volume)
                if vwap_series is None or vwap_series.empty: return
                
                current_vwap = vwap_series.iloc[-1]

                # ENTRY LOGIC
                if current_price > range_data['high'] and current_price > current_vwap:
                    qty = self.risk.calculate_quantity(current_price)
                    res = self.order_manager.place_intraday_order(symbol, token, qty, "BUY")
                    
                    if res['status'] == "success":
                        self.active_positions[token] = {'qty': qty, 'entry': current_price}
                        self.risk.current_trades += 1
            except Exception as e:
                print(f"⚠️ Strategy Calculation Error: {e}")

    def calculate_orb(self, symbol_token):
        df = self.get_historical_data(symbol_token)
        if df is not None and len(df) >= 15:
            orb_df = df.head(15)
            self.opening_range[symbol_token] = {
                "high": orb_df['high'].max(),
                "low": orb_df['low'].min()
            }
            return self.opening_range[symbol_token]
        return None

    def _manage_exit_logic(self, symbol, token, ltp):
        pos = self.active_positions[token]
        target = pos['entry'] * 1.015
        sl = pos['entry'] * 0.99

        if ltp >= target or ltp <= sl:
            self.order_manager.place_intraday_order(symbol, token, pos['qty'], "SELL")
            del self.active_positions[token]

    def scan_markets(self):
        # Simplified for testing
        return [{"symbol": "ZOMATO", "token": "15590"}, {"symbol": "TATAMOTORS", "token": "3456"}]