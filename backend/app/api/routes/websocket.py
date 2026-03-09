import uuid
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.api.websocket_manager import ws_manager
from app.core.services.auth_service import decode_token

router = APIRouter(tags=["WebSocket"])
logger = logging.getLogger(__name__)


@router.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket,
    token: str = Query(None),
):
    client_id = str(uuid.uuid4())

    # Optionally verify token
    user_id = None
    if token:
        payload = decode_token(token)
        if payload:
            user_id = payload.get("sub")

    await ws_manager.connect(websocket, client_id)
    try:
        # Send welcome message
        await ws_manager.send_personal(
            {"type": "CONNECTED", "data": {"client_id": client_id, "user_id": user_id}},
            client_id,
        )
        while True:
            data = await websocket.receive_text()
            try:
                msg = json.loads(data)
                if msg.get("type") == "PING":
                    await ws_manager.send_personal({"type": "PONG"}, client_id)
            except Exception:
                pass
    except WebSocketDisconnect:
        ws_manager.disconnect(client_id)
