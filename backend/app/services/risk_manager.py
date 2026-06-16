class RiskManager:
    def __init__(self, total_capital=10000):
        # Configuration based on your documentation
        self.total_capital = total_capital
        self.max_daily_loss = 200      # 2% of ₹10,000
        self.max_trades_per_day = 3    # User can change this from UI later
        
        # Current State
        self.current_trades = 0
        self.current_mtm = 0.0         # Current profit/loss for the day
        self.is_kill_switch_active = False

    def can_trade(self):
        """Checks all risk rules before allowing a trade"""
        if self.is_kill_switch_active:
            return False, "Kill switch is active"

        if self.current_trades >= self.max_trades_per_day:
            return False, f"Daily trade limit ({self.max_trades_per_day}) reached"

        if self.current_mtm <= -self.max_daily_loss:
            return False, f"Max daily loss (₹{self.max_daily_loss}) exceeded. Trading halted."

        return True, "Rules cleared"

    def calculate_quantity(self, stock_price):
        """
        Calculates quantity using 5x Intraday Leverage.
        Logic: Use 50% of capital per trade to allow for diversification.
        """
        usable_capital_per_trade = self.total_capital / 2  # ₹5,000
        leveraged_buying_power = usable_capital_per_trade * 5  # ₹25,000
        
        quantity = int(leveraged_buying_power / stock_price)
        
        # Ensure we buy at least 1 share
        return max(quantity, 1)

    def update_pnl(self, trade_pnl):
        """Updates the daily Mark-to-Market"""
        self.current_mtm += trade_pnl
        print(f"📉 MTM Updated: ₹{self.current_mtm}")

    def activate_kill_switch(self):
        """Stops the bot immediately"""
        self.is_kill_switch_active = True
        print("🚨 RISK MANAGER: KILL SWITCH ACTIVATED!")