from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from app.services.connection_manager import ui_manager

router = APIRouter()

@router.websocket("/live")
async def websocket_endpoint(websocket: WebSocket):
    await ui_manager.connect(websocket)
    try:
        while True:
            # Keep connection alive by waiting for any message
            await websocket.receive_text()
    except WebSocketDisconnect:
        ui_manager.disconnect(websocket)