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
        self.watchlist = [] # Stocks selected via React UI
        self.is_running = False
        self._stop_event = False  
        self.streamer_started = False 

    async def initialize(self):
        """Step 1: Broker Login & Service Setup"""
        try:
            logger.info("🔧 Initializing AlphaTrade Engine...")
            self.api, jwt_token = self.auth.login()
            
            if self.api:
                # 1. Initialize Strategy Brain
                self.strategy = StrategyService(self.api, capital=10000)
                
                # 2. Initialize Streamer Eyes (Pass strategy instance for event-triggering)
                self.streamer = DataStreamer(self.api, self.strategy)
                
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
        # return True # Uncomment this for testing at night
        return time(9, 15) <= now <= time(15, 30)

    async def run_forever(self):
        """
        THE MANAGER LOOP: 
        This loop now ONLY handles UI updates and status monitoring.
        Strategy execution is handled by the WebSocket Events in streamer.py.
        """
        if not await self.initialize():
            logger.error("🛑 System could not start. Check credentials.")
            return

        logger.info("🚀 AlphaTrade Manager is active.")

        while not self._stop_event:
            try:
                # 1. UI HEARTBEAT: Push State to React Dashboard
                # We fetch latest prices from bot_state (updated by WebSocket)
                await ui_manager.broadcast({
                    "type": "SYSTEM_UPDATE",
                    "status": "OPERATIONAL" if self.is_running else "OFFLINE",
                    "active_trades": len(self.strategy.active_positions),
                    "pnl": round(self.strategy.risk.current_mtm, 2),
                    "margin": self.strategy.risk.total_capital,
                    "watchlist_count": len(self.watchlist),
                    "prices": bot_state.latest_prices 
                })

                # 2. MARKET HOURS CHECK
                if not self.is_market_open():
                    if self.streamer_started:
                        logger.info("🕒 Market Closed. Stopping background stream.")
                        self.stop() # Graceful exit at 3:30 PM
                
                # 3. WAITING FOR USER INPUT
                if self.is_market_open() and not self.watchlist:
                    # In this version, we wait for the user to deploy 5 stocks via React
                    pass 

                # 4. BREATHE: We sleep longer because the heavy lifting 
                # is happening in the WebSocket thread, not here.
                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"⚠️ Manager Loop Error: {e}")
                await asyncio.sleep(5)

# Create a single instance to be imported by main.py
orchestrator = AlphaTradeOrchestrator()