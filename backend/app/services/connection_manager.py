from fastapi import WebSocket
from typing import List

class ConnectionManager:
    def __init__(self):
        # Stores all active browser connections
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        """Sends JSON data to all connected React Dashboards"""
        for connection in self.active_connections:
            try:
                # Use the built-in FastAPI method - it's the cleanest way
                await connection.send_json(message)
            except Exception:
                self.active_connections.remove(connection)

# Create the global instance to be used by the Broker Stream and the API
ui_manager = ConnectionManager()