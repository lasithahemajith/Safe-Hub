import json
import logging
from typing import Dict, List
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        logger.info(f"WebSocket connected: {client_id}")

    def disconnect(self, client_id: str):
        self.active_connections.pop(client_id, None)
        logger.info(f"WebSocket disconnected: {client_id}")

    async def send_personal(self, message: dict, client_id: str):
        ws = self.active_connections.get(client_id)
        if ws:
            try:
                await ws.send_text(json.dumps(message))
            except Exception as e:
                logger.error(f"Error sending to {client_id}: {e}")
                self.disconnect(client_id)

    async def broadcast(self, message: dict):
        disconnected = []
        for client_id, ws in self.active_connections.items():
            try:
                await ws.send_text(json.dumps(message))
            except Exception:
                disconnected.append(client_id)
        for client_id in disconnected:
            self.disconnect(client_id)

    async def broadcast_new_incident(self, incident: dict):
        await self.broadcast({
            "type": "NEW_INCIDENT",
            "data": incident,
        })

    async def broadcast_incident_update(self, incident: dict):
        await self.broadcast({
            "type": "INCIDENT_UPDATED",
            "data": incident,
        })

    async def broadcast_alert(self, alert: dict):
        await self.broadcast({
            "type": "NEW_ALERT",
            "data": alert,
        })


ws_manager = ConnectionManager()
