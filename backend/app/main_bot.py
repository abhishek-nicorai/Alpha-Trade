import asyncio
from datetime import datetime, time
import logging

# Modular Imports
from app.services.broker import AuthManager
from app.services.strategy import StrategyService
from app.services.streamer import DataStreamer
from app.services.connection_manager import ui_manager
from app.state import bot_state

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AlphaTrade")

class AlphaTradeOrchestrator:
    def __init__(self):
        self.auth = AuthManager()
        self.api = None
        self.strategy = None
        self.streamer = None
        self.watchlist = []
        self.is_running = False
        self._stop_event = False  
        self.streamer_started = False # Track if background thread is active

    async def initialize(self):
        """Step 1: Broker Login & Service Setup"""
        try:
            logger.info("🔧 Initializing AlphaTrade Engine...")
            self.api, jwt_token = self.auth.login()
            
            if self.api:
                # Initialize Brain (Strategy) and Eyes (Streamer)
                self.strategy = StrategyService(self.api, capital=10000)
                self.streamer = DataStreamer(self.api)
                self.is_running = True
                return True
            return False
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            return False

    def stop(self):
        """Gracefully stops the background loop and closes connections"""
        logger.info("🛑 Shutting down AlphaTrade Engine...")
        self._stop_event = True
        self.is_running = False
        if self.streamer and self.streamer.sws:
            try:
                self.streamer.sws.close()
            except:
                pass

    def is_market_open(self):
        """Check if time is between 09:15 and 15:30 IST"""
        now = datetime.now().time()
        # For night testing, you can temporarily return True
        return time(9, 15) <= now <= time(15, 30)

    async def run_forever(self):
        """The Main Master Loop"""
        if not await self.initialize():
            logger.error("🛑 System could not start. Check your credentials.")
            return

        logger.info("🚀 AlphaTrade Bot is now LIVE and monitoring.")

        while not self._stop_event:
            try:
                # 1. UI HEARTBEAT: Always keep React updated
                # We send the list of symbols being watched so the Dashboard can show names
                await ui_manager.broadcast({
                    "type": "SYSTEM_UPDATE",
                    "status": "OPERATIONAL" if self.is_running else "OFFLINE",
                    "active_trades": len(self.strategy.active_positions) if self.strategy else 0,
                    "pnl": self.strategy.risk.current_mtm if self.strategy else 0.0,
                    "margin": self.strategy.risk.total_capital if self.strategy else 10000,
                    "watchlist_symbols": [s['symbol'] for s in self.watchlist]
                })

                if self.is_market_open():
                    # 2. SCANNER LOGIC: Populate Watchlist
                    if not self.watchlist:
                        logger.info("🔍 Running Market Intelligence Scanner...")
                        self.watchlist = self.strategy.scan_markets()
                        
                        # FALLBACK: If scanner empty, use defaults
                        if not self.watchlist:
                            logger.warning("⚠️ No Open=Low stocks. Adding Fallbacks.")
                            self.watchlist = [
                                {"symbol": "ZOMATO", "token": "15590"},
                                {"symbol": "TATAMOTORS", "token": "3456"}
                            ]
                    
                    # 3. STREAMER START: Launch background thread ONCE
                    if self.watchlist and not self.streamer_started:
                        tokens = [{"exchangeType": 1, "tokens": [s['token'] for s in self.watchlist]}]
                        logger.info(f"🧵 Starting Background Data Thread for: {tokens}")
                        # This method in streamer.py now uses threading.Thread
                        self.streamer.connect_and_watch(tokens)
                        self.streamer_started = True

                    # 4. STRATEGY CHECK: Iterate through shared memory
                    for stock in self.watchlist:
                        token = stock['token']
                        symbol = stock['symbol']
                        
                        # Get live price from the 'Eyes' (updated by the background thread)
                        current_price = bot_state.latest_prices.get(token)
                        
                        if current_price:
                            self.strategy.check_for_signals(symbol, token, current_price)

                else:
                    logger.info("😴 Market is Closed. Bot in standby.")

                # Breathe time (2 seconds is standard for retail bots)
                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"⚠️ Master Loop Error: {e}")
                await asyncio.sleep(5)

# Global Instance
orchestrator = AlphaTradeOrchestrator()