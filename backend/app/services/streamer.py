import os
import threading
import logging
import json
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from app.state import bot_state

logger = logging.getLogger("AlphaTrade")

class DataStreamer:
    def __init__(self, smart_api, strategy_service):
        """
        strategy_service: The instance of StrategyService to trigger events
        """
        self.smart_api = smart_api
        self.strategy = strategy_service # The 'Brain' of the bot
        
        self.client_id = os.getenv("CLIENT_ID")
        self.api_key = os.getenv("API_KEY")
        self.jwt_token = self.smart_api.access_token 
        self.feed_token = self.smart_api.feed_token
        
        self.tokens_to_watch = []
        self.token_symbol_map = {} # Maps Token ID -> Symbol Name
        self.sws = None
        self.thread = None

    def set_watchlist(self, watchlist):
        """
        Updates the internal map so the streamer knows that 
        Token '15590' belongs to 'ZOMATO'
        """
        self.token_symbol_map = {item['token']: item['symbol'] for item in watchlist}
        self.tokens_to_watch = [{"exchangeType": 1, "tokens": [item['token'] for item in watchlist]}]

    def on_data(self, ws, msg):
        """
        EVENT TRIGGER: This runs every time a price tick arrives.
        It is the heartbeat of your event-driven system.
        """
        token = msg.get('token')
        lp = msg.get('last_traded_price')
        
        if token and lp:
            price = lp / 100
            symbol = self.token_symbol_map.get(token)

            if symbol:
                # 1. Update shared state (Thread-safe memory)
                bot_state.update_price(token, symbol, price)
                
                # 2. TRIGGER STRATEGY EVALUATION (The Event)
                # Instead of the bot looping, the tick 'pushes' the logic
                self.strategy.check_for_signals(symbol, token, price)

    def on_open(self, ws):
        logger.info("📡 WebSocket Connection Established with NSE.")
        correlation_id = "alphatrade_v1"
        
        if self.tokens_to_watch:
            # Subscribe to the 5 stocks you selected in React
            self.sws.subscribe(correlation_id, 1, self.tokens_to_watch)
            logger.info(f"📡 Subscribed to: {self.token_symbol_map.values()}")

    def on_error(self, ws, error):
        logger.error(f"❌ WebSocket Feed Error: {error}")

    def connect_and_watch(self, watchlist):
        """
        Handles (re)connection and starts the background thread.
        """
        self.set_watchlist(watchlist)
        
        if not self.feed_token:
            logger.error("❌ Cannot start stream: Feed Token missing.")
            return

        # If already running, we close the old one before starting fresh
        if self.sws:
            try:
                self.sws.close()
            except:
                pass

        # Initialize WebSocket with credentials
        self.sws = SmartWebSocketV2(
            self.jwt_token, 
            self.api_key, 
            self.client_id, 
            self.feed_token
        )
        
        self.sws.on_open = self.on_open
        self.sws.on_data = self.on_data
        self.sws.on_error = self.on_error

        # Start the background thread
        # daemon=True ensures the thread dies when you stop the main server
        self.thread = threading.Thread(target=self._run_websocket, daemon=True)
        self.thread.start()
        logger.info(f"🧵 Background Stream Thread started for {len(watchlist)} stocks.")

    def _run_websocket(self):
        try:
            self.sws.connect()
        except Exception as e:
            logger.error(f"🧵 Thread Crash: {e}")