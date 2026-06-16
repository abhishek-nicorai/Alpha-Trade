from fastapi import APIRouter, Depends
from pydantic import BaseModel
from app.db.session import SessionLocal
from app.db import models

router = APIRouter()

class SettingsUpdate(BaseModel):
    capital: float
    max_trades: int

@router.post("/update")
async def update_settings(data: SettingsUpdate):
    db = SessionLocal()
    # Check if config exists, if not create it
    config = db.query(models.Config).first()
    if not config:
        config = models.Config(capital=data.capital, max_trades=data.max_trades)
        db.add(config)
    else:
        config.capital = data.capital
        config.max_trades = data.max_trades
    
    db.commit()
    db.close()
    return {"message": "Settings synced successfully"}