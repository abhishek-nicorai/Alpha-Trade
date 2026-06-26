from fastapi import APIRouter
from app.api.v1.endpoints import dashboard, market, ws, settings, trades , watchlist 
api_router = APIRouter()

# Include the dashboard router
api_router.include_router(dashboard.router, tags=["Dashboard"])
api_router.include_router(market.router, prefix="/market", tags=["Market"])
api_router.include_router(ws.router, prefix="/ws", tags=["Websocket"])
api_router.include_router(settings.router, prefix="/settings", tags=["Settings"])
api_router.include_router(trades.router, prefix="/trades", tags=["Trades"])
api_router.include_router(watchlist.router, prefix="/watchlist", tags=["Watchlist"])