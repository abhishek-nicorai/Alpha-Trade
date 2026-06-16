import requests
import json
import os

class ScriptManager:
    def __init__(self):
        self.url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
        self.file_path = "scrip_master.json"
        self.all_stocks = []

    def download_scrip_master(self):
        """Downloads the latest list of all 5000+ stocks from Angel One"""
        print("📥 Downloading latest Scrip Master (All NSE Stocks)...")
        response = requests.get(self.url)
        if response.status_code == 200:
            with open(self.file_path, "w") as f:
                f.write(response.text)
            print("✅ Download Complete.")
            self.load_local_scrip()
        else:
            print("❌ Failed to download Scrip Master")

    def load_local_scrip(self):
        """Loads and filters only NSE Equities (No options/futures)"""
        if not os.path.exists(self.file_path):
            self.download_scrip_master()
            return

        with open(self.file_path, "r") as f:
            data = json.load(f)
            # Filter for NSE Stocks (Equity) only
            self.all_stocks = [
                {"symbol": s['symbol'], "token": s['token'], "name": s['name']}
                for s in data 
                if s['exch_seg'] == 'NSE' and s['symbol'].endswith('-EQ')
            ]
        print(f"📖 Loaded {len(self.all_stocks)} NSE stocks into memory.")

    def search_stock(self, query):
        """Search through all 5,000 stocks instantly"""
        query = query.upper()
        results = [s for s in self.all_stocks if query in s['symbol']]
        return results[:10] # Return top 10 matches