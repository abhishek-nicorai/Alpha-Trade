import pandas as pd
import time as sleep_timer
from app.services.script_manager import ScriptManager

class MarketService:
    def __init__(self, broker_client):
        self.api = broker_client
        self.script_manager = ScriptManager()
        self.script_manager.load_local_scrip()

    def get_dynamic_universe(self, limit=30):
        """
        Instead of hardcoding, we pull the first 'N' stocks from the 
        official Scrip Master. You can change this to filter by 
        Sector, Index (Nifty 50), or Volume.
        """
        # We take the top stocks from the loaded 5000+ list
        # In a real-world scenario, you could filter for NIFTY 100 symbols here.
        return self.script_manager.all_stocks[:limit]

    def get_real_movers(self):
        """Calculates movers for a DYNAMIC universe of stocks"""
        scored_stocks = []
        
        # Get 30 stocks dynamically from the master list
        dynamic_list = self.get_dynamic_universe(limit=30)
        
        print(f"📡 Dynamic Scanner: Scanning {len(dynamic_list)} NSE stocks...")

        for stock in dynamic_list:
            try:
                # We use f"{stock['symbol']}" because the scrip master 
                # already contains the full trading symbol (e.g., 'RELIANCE-EQ')
                res = self.api.ltpData("NSE", stock['symbol'], stock['token'])
                
                if res['status'] and res['data']:
                    ltp = float(res['data']['ltp'])
                    close = float(res['data']['close'])
                    
                    if close > 0:
                        change = ((ltp - close) / close) * 100
                        scored_stocks.append({
                            "symbol": stock['symbol'].replace("-EQ", ""), # Clean name for UI
                            "token": stock['token'],
                            "change": round(change, 2),
                            "ltp": ltp
                        })
                
                # Still need a tiny sleep to respect API limits
                sleep_timer.sleep(0.05) 
            except:
                continue

        # Sort all 30+ stocks to find the winners and losers
        gainers = sorted(scored_stocks, key=lambda x: x['change'], reverse=True)
        losers = sorted(scored_stocks, key=lambda x: x['change'])
        
        return {
            "gainers": gainers[:5],
            "losers": losers[:5]
        }