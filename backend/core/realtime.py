"""Board events over WebSocket.

Every change on a board is published to the Redis channel `board:<id>`. Each app process listens
to all board channels and forwards messages to the WebSockets connected to it. This way two users
connected to different workers still see each other's changes.

Without REDIS_URL (tests, quick local runs) events go straight to local connections.
"""

import asyncio
import json
import logging
from collections import defaultdict

from fastapi import WebSocket
from redis.asyncio import Redis

from core import settings

logger = logging.getLogger(__name__)


class Broadcaster:
    def __init__(self, redis_url: str = ''):
        self.redis_url = redis_url
        self.redis: Redis | None = None
        self.connections: dict[int, set[WebSocket]] = defaultdict(set)
        self.listener: asyncio.Task | None = None

    async def start(self):
        if not self.redis_url:
            return
        self.redis = Redis.from_url(self.redis_url)
        self.listener = asyncio.create_task(self.listen())

    async def stop(self):
        if self.listener:
            self.listener.cancel()
        if self.redis:
            await self.redis.aclose()

    def connect(self, board_id: int, websocket: WebSocket):
        self.connections[board_id].add(websocket)

    def disconnect(self, board_id: int, websocket: WebSocket):
        self.connections[board_id].discard(websocket)
        if not self.connections[board_id]:
            del self.connections[board_id]

    async def publish(self, board_id: int, event: str, data: dict, actor_id: int | None = None):
        message = json.dumps({'event': event, 'board_id': board_id, 'actor_id': actor_id, 'data': data})
        if self.redis:
            await self.redis.publish(f'board:{board_id}', message)
        else:
            await self.send_local(board_id, message)

    async def send_local(self, board_id: int, message: str):
        for websocket in list(self.connections.get(board_id, ())):
            try:
                await websocket.send_text(message)
            except Exception:
                # The client went away without closing properly
                self.disconnect(board_id, websocket)

    async def listen(self):
        pubsub = self.redis.pubsub()
        await pubsub.psubscribe('board:*')
        try:
            async for message in pubsub.listen():
                if message['type'] != 'pmessage':
                    continue
                board_id = int(message['channel'].decode().split(':')[1])
                await self.send_local(board_id, message['data'].decode())
        except asyncio.CancelledError:
            await pubsub.aclose()
            raise
        except Exception:
            logger.exception('Redis listener stopped')


broadcaster = Broadcaster(settings.REDIS_URL)
