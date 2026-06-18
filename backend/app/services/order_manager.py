import os
from datetime import datetime
from app.db.session import SessionLocal
from app.db import models
from app.state import bot_state  # Use live memory for faster execution

class OrderManager:
    def __init__(self, broker_client):
        self.api = broker_client
        # SAFETY FIRST: Set to True for virtual trading. 
        # Change to False only when you want to use real money.
        self.IS_PAPER_TRADING = True 

    def place_intraday_order(self, symbol, token, qty, side):
        """
        Main method to handle order execution (Paper or Live)
        symbol: e.g., 'ZOMATO'
        side: 'BUY' or 'SELL'
        """
        # 1. Format symbol for Angel One NSE standard
        tradingsymbol = f"{symbol}-EQ" if not symbol.endswith("-EQ") else symbol
        
        print(f"📦 Attempting {side} for {tradingsymbol} | Qty: {qty}")

        try:
            order_id = "MOCK_ORDER_ID" 
            execution_price = 0.0

            # 2. Get Execution Price from Shared Memory (Fastest & avoids API errors)
            execution_price = bot_state.latest_prices.get(token, 0.0)

            # 3. Fallback: If memory is empty, try a quick API call
            if execution_price == 0.0:
                try:
                    ltp_res = self.api.ltpData("NSE", tradingsymbol, token)
                    if ltp_res['status'] and ltp_res.get('data'):
                        execution_price = float(ltp_res['data']['ltp'])
                except:
                    print(f"⚠️ Could not get LTP for {symbol}, using fallback 0.0")

            # 4. Handle Real Trading
            if not self.IS_PAPER_TRADING:
                order_params = {
                    "variety": "NORMAL",
                    "tradingsymbol": tradingsymbol,
                    "symboltoken": token,
                    "transactiontype": side,
                    "exchange": "NSE",
                    "ordertype": "MARKET",
                    "producttype": "INTRADAY",
                    "duration": "DAY",
                    "quantity": str(qty)
                }
                order_res = self.api.placeOrder(order_params)
                if order_res['status']:
                    order_id = order_res['data']['orderid']
                    print(f"🔥 LIVE ORDER PLACED: {order_id}")
                else:
                    raise Exception(f"Broker Rejected: {order_res.get('message')}")

            # 5. Log to Database (Stops the infinite loop)
            self._log_to_db(symbol, qty, side, execution_price, order_id)

            return {"status": "success", "order_id": order_id, "price": execution_price}

        except Exception as e:
            print(f"❌ Order Execution Failed for {symbol}: {str(e)}")
            return {"status": "error", "message": str(e)}

    def _log_to_db(self, symbol, qty, side, price, order_id):
        """Internal method to save trade history to SQLite"""
        db = SessionLocal()
        try:
            new_trade = models.Trade(
                symbol=symbol,
                qty=qty,
                side=side,
                entry_price=float(price),
                order_id=str(order_id),
                timestamp=datetime.utcnow()
            )
            db.add(new_trade)
            db.commit()
            print(f"💾 Trade logged to Database: {symbol} at ₹{price}")
        except Exception as e:
            print(f"💾 DB Log Error: {e}")
            db.rollback()
        finally:
            db.close()