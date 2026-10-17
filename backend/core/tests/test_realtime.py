import asyncio
import json
import os

import pytest

from core.realtime import Broadcaster

REDIS_URL = os.getenv('TEST_REDIS_URL', '')


class FakeSocket:
    def __init__(self, broken=False):
        self.messages = asyncio.Queue()
        self.broken = broken

    async def send_text(self, text):
        if self.broken:
            raise RuntimeError('connection lost')
        await self.messages.put(json.loads(text))


async def test_local_mode_delivers_to_board_connections():
    broadcaster = Broadcaster()
    here, elsewhere = FakeSocket(), FakeSocket()
    broadcaster.connect(1, here)
    broadcaster.connect(2, elsewhere)

    await broadcaster.publish(1, 'task.created', {'id': 5}, actor_id=7)

    assert await here.messages.get() == {'event': 'task.created', 'board_id': 1, 'actor_id': 7, 'data': {'id': 5}}
    assert elsewhere.messages.empty()


async def test_broken_socket_is_dropped():
    broadcaster = Broadcaster()
    broadcaster.connect(1, FakeSocket(broken=True))

    await broadcaster.publish(1, 'task.created', {})

    assert 1 not in broadcaster.connections


@pytest.mark.skipif(not REDIS_URL, reason='set TEST_REDIS_URL to run Redis tests')
async def test_events_reach_sockets_on_another_process():
    """Two broadcasters stand for two app workers. An event published on one reaches a socket on the other."""
    worker_a, worker_b = Broadcaster(REDIS_URL), Broadcaster(REDIS_URL)
    await worker_a.start()
    await worker_b.start()
    socket_on_b = FakeSocket()
    worker_b.connect(42, socket_on_b)
    try:
        await asyncio.sleep(0.2)  # let both listeners subscribe

        await worker_a.publish(42, 'task.moved', {'id': 1})

        event = await asyncio.wait_for(socket_on_b.messages.get(), timeout=3)
        assert (event['event'], event['board_id']) == ('task.moved', 42)
    finally:
        await worker_a.stop()
        await worker_b.stop()
