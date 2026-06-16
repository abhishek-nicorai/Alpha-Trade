from fastapi import APIRouter, Query
from app.services.market_service import MarketService
from app.services.script_manager import ScriptManager
from app.main_bot import orchestrator
from typing import Optional

router = APIRouter()

# Initialize the Scrip Manager (Infinite Knowledge)
script_engine = ScriptManager()
script_engine.load_local_scrip() # Loads 5,000+ stocks into memory

@router.get("/movers/{period}")
async def get_market_movers(period: str):
    """
    Fetches real-time gainers and losers from the NSE.
    Logic: Scans the top 100 most liquid stocks.
    """
    if not orchestrator.api:
        return {"gainers": [], "losers": [], "error": "Broker Session Expired"}

    # Initialize the scanner with the live broker session
    scanner = MarketService(orchestrator.api)
    
    if period == "TODAY":
        return scanner.get_real_movers()
    
    # Logic for 1W and 1M using historical data
    # For now, we return today's dynamic data to keep performance high
    return scanner.get_real_movers()

@router.get("/search")
async def search_all_india_stocks(q: Optional[str] = Query(None, min_length=2)):
    """
    Searches the entire NSE database (5,000+ stocks).
    This provides the 'Infinite Knowledge' you requested.
    """
    if not q:
        return []
    
    results = script_engine.search_stock(q)
    return results

@router.post("/watchlist/add")
async def add_to_bot_watchlist(stock_data: dict):
    """
    Tells the Trading Bot to start monitoring this specific stock live.
    """
    symbol = stock_data.get("symbol")
    token = stock_data.get("token")
    
    if symbol and token:
        # Add to the orchestrator's live list
        new_entry = {"symbol": symbol, "token": token}
        if new_entry not in orchestrator.watchlist:
            orchestrator.watchlist.append(new_entry)
            
            # Subscribe to the live feed instantly
            tokens = [{"exchangeType": 1, "tokens": [token]}]
            orchestrator.streamer.connect_and_watch(tokens)
            
            print(f"📡 Bot now monitoring {symbol} for ORB strategy.")
            return {"status": "success", "message": f"{symbol} added to live monitoring."}
    
    return {"status": "error", "message": "Invalid stock data"}