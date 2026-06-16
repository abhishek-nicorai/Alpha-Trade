import os
import threading
import logging
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
from app.state import bot_state

logger = logging.getLogger("AlphaTrade")

class DataStreamer:
    def __init__(self, smart_api):
        self.smart_api = smart_api
        self.client_id = os.getenv("CLIENT_ID")
        self.api_key = os.getenv("API_KEY")
        self.jwt_token = self.smart_api.access_token 
        self.feed_token = self.smart_api.feed_token
        
        self.tokens_to_watch = []
        self.sws = None
        self.thread = None # To store our background thread

    def on_data(self, ws, msg):
        token = msg.get('token')
        lp = msg.get('last_traded_price')
        if token and lp:
            price = lp / 100
            # Update Shared State so the main thread can see the price
            bot_state.latest_prices[token] = price
            # logger.info(f"Tick: {token} -> {price}")

    def on_open(self, ws):
        logger.info("📡 WebSocket Connection Opened!")
        correlation_id = "alphatrade_v1"
        # Subscribe to tokens (Mode 1 = LTP)
        self.sws.subscribe(correlation_id, 1, self.tokens_to_watch)

    def on_error(self, ws, error):
        logger.error(f"❌ WebSocket Error: {error}")

    def connect_and_watch(self, token_list):
        """Starts the WebSocket in a BACKGROUND THREAD"""
        self.tokens_to_watch = token_list
        
        if not self.feed_token:
            logger.error("❌ Feed Token missing!")
            return

        # Initialize WebSocket
        self.sws = SmartWebSocketV2(self.jwt_token, self.api_key, self.client_id, self.feed_token)
        self.sws.on_open = self.on_open
        self.sws.on_data = self.on_data
        self.sws.on_error = self.on_error

        # --- THE THREADING PART ---
        # We create a thread to run the 'connect' function
        self.thread = threading.Thread(target=self._run_websocket, daemon=True)
        self.thread.start()
        logger.info("🧵 WebSocket Thread Started in Background")

    def _run_websocket(self):
        """Internal method to trigger connection"""
        try:
            self.sws.connect()
        except Exception as e:
            logger.error(f"WebSocket Thread Crash: {e}")