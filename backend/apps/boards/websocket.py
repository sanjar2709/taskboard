from fastapi import APIRouter, WebSocket, WebSocketDisconnect, status

from core.db import SessionLocal
from core.realtime import broadcaster
from core.security import decode_token

from .models import Board

router = APIRouter()


@router.websocket('/boards/{board_id}/ws')
async def board_events(websocket: WebSocket, board_id: int, token: str = ''):
    # Browsers can't send headers with a WebSocket, so the access token comes as ?token=
    user_id = decode_token(token, 'access')
    async with SessionLocal() as db:
        board = await db.get(Board, board_id)
        is_member = board is not None and any(m.user_id == user_id for m in board.members)
    if user_id is None or not is_member:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    await websocket.accept()
    broadcaster.connect(board_id, websocket)
    try:
        while True:
            # Clients only listen; incoming text is used as a keep-alive ping
            if await websocket.receive_text() == 'ping':
                await websocket.send_text('pong')
    except WebSocketDisconnect:
        pass
    finally:
        broadcaster.disconnect(board_id, websocket)
