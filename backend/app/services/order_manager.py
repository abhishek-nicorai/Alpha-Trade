import os
from app.db.session import SessionLocal
from app.db import models
from datetime import datetime

class OrderManager:
    def __init__(self, broker_client):
        self.api = broker_client
        # SAFETY FIRST: Set this to True for testing without real money
        self.IS_PAPER_TRADING = True 

    def place_intraday_order(self, symbol, token, qty, side):
        # 1. FORCE NSE Standard: ZOMATO -> ZOMATO-EQ
        if not symbol.endswith("-EQ"):
            tradingsymbol = f"{symbol}-EQ"
        else:
            tradingsymbol = symbol
        
        print(f"📦 Attempting {side} for {tradingsymbol} | Qty: {qty}")

        try:
            order_id = "MOCK_ORDER_ID" 
            execution_price = 0.0

            # 2. Get Live Price (Standard Angel One Method)
            ltp_res = self.api.ltpData("NSE", tradingsymbol, token)
            
            # 3. Defensive Check: Ensure response is valid
            if ltp_res and ltp_res.get('status') is True and ltp_res.get('data'):
                execution_price = float(ltp_res['data']['ltp'])
            else:
                # If API fails, we use a dummy price for paper trading so the bot doesn't loop
                print(f"⚠️ API Error: {ltp_res.get('message') if ltp_res else 'No Response'}")
                execution_price = 0.0 

            # 4. Handle Real Trading vs Paper Trading
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

            # 5. Log to Database
            self._log_to_db(symbol, qty, side, execution_price, order_id)
            return {"status": "success", "order_id": order_id, "price": execution_price}

        except Exception as e:
            print(f"❌ Order Execution Failed: {str(e)}")
            return {"status": "error", "message": str(e)}
        # Ensure the symbol has the correct suffix for NSE Equity
        formatted_symbol = f"{symbol}-EQ" if not symbol.endswith("-EQ") else symbol
        
        print(f"📦 Attempting {side} for {formatted_symbol} | Qty: {qty}")

        try:
            order_id = "MOCK_ORDER_ID" 
            execution_price = 0.0

            # 1. Get Live Price for the trade record
            # We use formatted_symbol (e.g., ZOMATO-EQ)
            ltp_res = self.api.ltpData("NSE", formatted_symbol, token)
            
            # 2. Safety Check: Ensure 'data' is not None before accessing it
            if ltp_res['status'] and ltp_res.get('data') is not None:
                execution_price = float(ltp_res['data']['ltp'])
            else:
                print(f"⚠️ Warning: Could not get live price for {formatted_symbol}. using 0.0")
                execution_price = 0.0

            # 3. Place the actual order (If not paper trading)
            if not self.IS_PAPER_TRADING:
                order_params = {
                    "variety": "NORMAL",
                    "tradingsymbol": formatted_symbol,
                    "symboltoken": token,
                    "transactiontype": side,
                    "exchange": "NSE",
                    "ordertype": "MARKET",
                    "producttype": "INTRADAY",
                    "duration": "DAY",
                    "quantity": str(qty)
                }
                order_id = self.api.placeOrder(order_params)

            # 4. Log to Database
            self._log_to_db(symbol, qty, side, execution_price, order_id)

            return {"status": "success", "order_id": order_id, "price": execution_price}

        except Exception as e:
            print(f"❌ Order Execution Failed for {symbol}: {e}")
            return {"status": "error", "message": str(e)}
        """
        Executes a trade and logs it to the database.
        side: 'BUY' or 'SELL'
        """
        print(f"📦 Attempting {side} for {symbol} | Qty: {qty}")

        try:
            order_id = "MOCK_ORDER_ID" # Default for paper trading
            execution_price = 0.0

            if not self.IS_PAPER_TRADING:
                # REAL TRADE LOGIC (Angel One API)
                order_params = {
                    "variety": "NORMAL",
                    "tradingsymbol": f"{symbol}-EQ",
                    "symboltoken": token,
                    "transactiontype": side,
                    "exchange": "NSE",
                    "ordertype": "MARKET",
                    "producttype": "INTRADAY",
                    "duration": "DAY",
                    "quantity": str(qty)
                }
                order_id = self.api.placeOrder(order_params)
            
            # For logs/UI, we fetch the LTP as the 'Execution Price'
            ltp_data = self.api.ltpData("NSE", symbol, token)
            execution_price = ltp_data['data']['ltp']

            # SAVE TO DATABASE (For your Trade Logs page)
            self._log_to_db(symbol, qty, side, execution_price, order_id)

            return {"status": "success", "order_id": order_id, "price": execution_price}

        except Exception as e:
            print(f"❌ Order Execution Failed: {e}")
            return {"status": "error", "message": str(e)}

    def _log_to_db(self, symbol, qty, side, price, order_id):
        """Internal method to save trade history"""
        db = SessionLocal()
        new_trade = models.Trade(
            symbol=symbol,
            qty=qty,
            side=side,
            entry_price=price,
            order_id=order_id,
            timestamp=datetime.utcnow()
        )
        db.add(new_trade)
        db.commit()
        db.close()
        print(f"💾 Trade logged to Database: {symbol} at ₹{price}")