from fastapi import APIRouter, HTTPException
from app.main_bot import orchestrator
from app.services.connection_manager import ui_manager

router = APIRouter()

@router.post("/sync")
async def sync_entire_watchlist(stocks: list):
    """
    Receives the 5 selected stocks from React and 
    injects them into the Trading Engine.
    """
    try:
        if not stocks:
            return {"status": "error", "message": "No stocks selected"}

        # 1. Update the Master Watchlist in the Orchestrator
        orchestrator.watchlist = stocks 
        
        # 2. Reset the Streamer so it picks up the new tokens
        # This stops old stocks and starts watching the new 5
        tokens = [{"exchangeType": 1, "tokens": [s['token'] for s in stocks]}]
        
        orchestrator.streamer_started = False 
        orchestrator.streamer.connect_and_watch(tokens)
        orchestrator.streamer_started = True

        # 3. Inform the UI that the bot is now tracking these specific stocks
        await ui_manager.broadcast({
            "type": "SYSTEM_MESSAGE",
            "message": f"Bot synced with {len(stocks)} stocks",
            "watchlist": [s['symbol'] for s in stocks]
        })

        print(f"✅ Watchlist Sync: Bot is now tracking {[s['symbol'] for s in stocks]}")
        return {"status": "success", "watchlist": orchestrator.watchlist}
        
    except Exception as e:
        print(f"❌ Sync Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))