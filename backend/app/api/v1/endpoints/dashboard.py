from fastapi import APIRouter

# 1. Create a router specifically for this file
router = APIRouter()

# 2. Use @router instead of @app
@router.get("/status")
def get_status():
    return {
        "status": "Active", 
        "broker": "Connected", 
        "pnl": 0.00
    }