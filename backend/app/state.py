# backend/app/state.py

class SharedState:
    def __init__(self):
        # Stores live prices: {"15590": 165.50, "3456": 480.10}
        self.latest_prices = {} 
        
        # Stores current Mark-to-Market P&L
        self.total_pnl = 0.0
        
        # Connection status
        self.is_broker_connected = False

# Create a single instance that all modules will import
bot_state = SharedState()