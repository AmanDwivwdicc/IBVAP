"""WebSocket connection manager for real-time updates."""

import json
from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    def __init__(self) -> None:
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def broadcast(self, message_type: str, data: dict[str, Any]) -> None:
        payload = json.dumps({"type": message_type, "data": data})
        dead: list[WebSocket] = []
        for connection in self.active_connections:
            try:
                await connection.send_text(payload)
            except Exception:
                dead.append(connection)
        for conn in dead:
            self.disconnect(conn)

    async def send_personal(self, websocket: WebSocket, message_type: str, data: dict[str, Any]) -> None:
        payload = json.dumps({"type": message_type, "data": data})
        await websocket.send_text(payload)


ws_manager = ConnectionManager()
