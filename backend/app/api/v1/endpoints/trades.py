from fastapi import APIRouter
from app.db.session import SessionLocal
from app.db import models
from typing import List

router = APIRouter()

@router.get("/history")
async def get_trade_history():
    db = SessionLocal()
    try:
        # Fetch all trades, most recent first
        trades = db.query(models.Trade).order_by(models.Trade.timestamp.desc()).all()
        
        # Calculate summary stats for the UI
        total_trades = len(trades)
        # Note: In a real app, you'd calculate actual P&L based on Exit Price
        
        return {
            "trades": trades,
            "summary": {
                "total_count": total_trades,
                "day_pnl": 0.0 # Placeholder for calculated daily MTM
            }
        }
    finally:
        db.close()