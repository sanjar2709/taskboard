import asyncio
import json
from contextlib import asynccontextmanager

import pytest
from httpx import AsyncClient
from httpx_ws import WebSocketDisconnect, aconnect_ws
from httpx_ws.transport import ASGIWebSocketTransport

from apps.common.tests.factories import auth, create_board_with, create_user
from core.security import create_access_token
from main import app


@asynccontextmanager
async def board_socket(board_id: int, token: str):
    # The transport has to be opened and closed in the same task, so this can't be a pytest fixture
    async with (
        AsyncClient(transport=ASGIWebSocketTransport(app=app), base_url='http://test/api/v1') as client,
        aconnect_ws(f'/boards/{board_id}/ws?token={token}', client) as ws,
    ):
        yield client, ws


async def next_event(ws) -> dict:
    return json.loads(await asyncio.wait_for(ws.receive_text(), timeout=3))


async def test_members_get_task_events():
    owner, member = await create_user(), await create_user()
    board = await create_board_with(owner, member)
    todo, _, done = (c.id for c in board.columns)

    async with board_socket(board.id, create_access_token(owner.id)) as (ws_client, ws):
        task = (await ws_client.post(f'/columns/{todo}/tasks', json={'title': 'A'}, headers=auth(member))).json()
        event = await next_event(ws)
        assert event['event'] == 'task.created'
        assert event['actor_id'] == member.id
        assert event['data']['title'] == 'A'

        await ws_client.post(f'/tasks/{task["id"]}/move', json={'column_id': done, 'index': 0}, headers=auth(member))
        event = await next_event(ws)
        assert event['event'] == 'task.moved'
        assert (event['data']['column_id'], event['data']['index']) == (done, 0)

        await ws_client.delete(f'/tasks/{task["id"]}', headers=auth(member))
        assert (await next_event(ws))['event'] == 'task.deleted'


async def test_column_and_member_events():
    owner = await create_user()
    await create_user(email='friend@example.com')
    board = await create_board_with(owner)

    async with board_socket(board.id, create_access_token(owner.id)) as (ws_client, ws):
        await ws_client.post(f'/boards/{board.id}/columns', json={'title': 'Review'}, headers=auth(owner))
        assert (await next_event(ws))['event'] == 'column.created'

        await ws_client.post(f'/boards/{board.id}/members', json={'email': 'friend@example.com'}, headers=auth(owner))
        event = await next_event(ws)
        assert event['event'] == 'member.added'
        assert event['data']['user']['email'] == 'friend@example.com'


async def test_events_stay_on_their_board():
    owner = await create_user()
    board = await create_board_with(owner)
    other = await create_board_with(owner, title='Other')

    async with board_socket(board.id, create_access_token(owner.id)) as (ws_client, ws):
        await ws_client.post(f'/columns/{other.columns[0].id}/tasks', json={'title': 'Elsewhere'}, headers=auth(owner))
        await ws_client.post(f'/columns/{board.columns[0].id}/tasks', json={'title': 'Here'}, headers=auth(owner))

        assert (await next_event(ws))['data']['title'] == 'Here'


async def test_ping():
    owner = await create_user()
    board = await create_board_with(owner)

    async with board_socket(board.id, create_access_token(owner.id)) as (ws_client, ws):
        await ws.send_text('ping')
        assert await ws.receive_text() == 'pong'


@pytest.mark.parametrize('who', ('stranger', 'bad_token'))
async def test_outsiders_are_rejected(who):
    owner, stranger = await create_user(), await create_user()
    board = await create_board_with(owner)
    token = create_access_token(stranger.id) if who == 'stranger' else 'garbage'

    # The transport runs in a task group, so the disconnect arrives wrapped in an exception group
    with pytest.raises(BaseExceptionGroup) as error:
        async with board_socket(board.id, token) as (_, ws):
            await ws.receive_text()

    assert error.group_contains(WebSocketDisconnect, match='', depth=None)
    disconnect = error.value.subgroup(WebSocketDisconnect).exceptions[0]
    while isinstance(disconnect, BaseExceptionGroup):
        disconnect = disconnect.exceptions[0]
    assert disconnect.code == 1008
