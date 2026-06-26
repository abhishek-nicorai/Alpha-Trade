import threading
import logging

logger = logging.getLogger("AlphaTrade")

class SharedState:
    def __init__(self):
        # The Lock is the 'Traffic Signal'. 
        # It ensures only one thread can modify data at a exact millisecond.
        self._lock = threading.Lock()

        # SCHEMA: { 
        #   "15590": {"symbol": "ZOMATO", "ltp": 160.50},
        #   "3456":  {"symbol": "TATAMOTORS", "ltp": 480.10}
        # }
        self.latest_prices = {} 
        
        self.total_pnl = 0.0
        self.is_broker_connected = False
        
        # To track which tokens have an active strategy evaluation running
        self.processing_tokens = set()

    def update_price(self, token, symbol, price):
        """
        Thread-safe method to update price. 
        Used by streamer.py when a new tick arrives.
        """
        with self._lock:
            self.latest_prices[token] = {
                "symbol": symbol,
                "ltp": float(price)
            }

    def get_price(self, token):
        """
        Thread-safe method to get a single price.
        """
        with self._lock:
            return self.latest_prices.get(token, {}).get("ltp", 0.0)

    def get_all_latest_data(self):
        """
        Returns a COPY of the latest prices.
        Critical for the UI Broadcast loop to prevent crashes.
        """
        with self._lock:
            return dict(self.latest_prices)

    def update_pnl(self, pnl):
        """Thread-safe P&L update"""
        with self._lock:
            self.total_pnl = round(pnl, 2)

# Create a single instance that all modules will import
bot_state = SharedState()