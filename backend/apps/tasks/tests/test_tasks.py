import pytest

from apps.common.tests.factories import auth, create_board_with, create_user


@pytest.fixture
async def setup():
    owner, member = await create_user(), await create_user()
    board = await create_board_with(owner, member)
    todo, progress, done = (c.id for c in board.columns)
    return owner, member, board, todo, progress, done


async def titles(client, board, user) -> dict[str, list[str]]:
    data = (await client.get(f'/boards/{board.id}', headers=auth(user))).json()
    return {c['title']: [t['title'] for t in c['tasks']] for c in data['columns']}


async def add(client, user, column_id, title, **extra) -> dict:
    return (await client.post(f'/columns/{column_id}/tasks', json={'title': title, **extra}, headers=auth(user))).json()


async def test_tasks_are_added_to_the_end(client, setup):
    owner, member, board, todo, *_ = setup

    for title in ('A', 'B', 'C'):
        await add(client, member, todo, title)

    assert (await titles(client, board, owner))['To do'] == ['A', 'B', 'C']


async def test_move_inside_column_and_between_columns(client, setup):
    owner, _, board, todo, progress, _ = setup
    a, b, c = [await add(client, owner, todo, t) for t in 'ABC']

    await client.post(f'/tasks/{c["id"]}/move', json={'column_id': todo, 'index': 0}, headers=auth(owner))
    assert (await titles(client, board, owner))['To do'] == ['C', 'A', 'B']

    await client.post(f'/tasks/{a["id"]}/move', json={'column_id': progress, 'index': 0}, headers=auth(owner))
    await client.post(f'/tasks/{b["id"]}/move', json={'column_id': progress, 'index': 0}, headers=auth(owner))
    result = await titles(client, board, owner)
    assert result['To do'] == ['C']
    assert result['In progress'] == ['B', 'A']


async def test_assign_only_to_members(client, setup):
    owner, member, _, todo, *_ = setup
    stranger = await create_user()

    task = await add(client, owner, todo, 'A', assignee_id=member.id, due_date='2026-11-01')
    assert task['assignee']['id'] == member.id
    assert task['due_date'] == '2026-11-01'

    response = await client.patch(f'/tasks/{task["id"]}', json={'assignee_id': stranger.id}, headers=auth(owner))
    assert response.status_code == 400
    data = {'title': 'B', 'assignee_id': stranger.id}
    response = await client.post(f'/columns/{todo}/tasks', json=data, headers=auth(owner))
    assert response.status_code == 400


async def test_update_and_delete(client, setup):
    owner, member, board, todo, *_ = setup
    task = await add(client, owner, todo, 'A')

    data = {'title': 'A2', 'description': 'details'}
    response = await client.patch(f'/tasks/{task["id"]}', json=data, headers=auth(member))
    assert response.json()['title'] == 'A2'
    assert (await client.get(f'/tasks/{task["id"]}', headers=auth(owner))).json()['description'] == 'details'

    assert (await client.delete(f'/tasks/{task["id"]}', headers=auth(member))).status_code == 204
    assert (await titles(client, board, owner))['To do'] == []


async def test_strangers_cannot_touch_tasks(client, setup):
    owner, _, _, todo, *_ = setup
    stranger = await create_user()
    task = await add(client, owner, todo, 'A')

    assert (await client.get(f'/tasks/{task["id"]}', headers=auth(stranger))).status_code == 404
    assert (await client.delete(f'/tasks/{task["id"]}', headers=auth(stranger))).status_code == 404
    assert (await client.post(f'/columns/{todo}/tasks', json={'title': 'x'}, headers=auth(stranger))).status_code == 404


async def test_cannot_move_task_to_another_board(client, setup):
    owner, _, _, todo, *_ = setup
    other_board = await create_board_with(owner, title='Other')
    task = await add(client, owner, todo, 'A')

    response = await client.post(
        f'/tasks/{task["id"]}/move', json={'column_id': other_board.columns[0].id, 'index': 0}, headers=auth(owner)
    )

    assert response.status_code == 400


async def test_move_to_missing_column(client, setup):
    owner, _, _, todo, *_ = setup
    task = await add(client, owner, todo, 'A')

    response = await client.post(f'/tasks/{task["id"]}/move', json={'column_id': 999, 'index': 0}, headers=auth(owner))

    assert response.status_code == 404


async def test_deleting_column_deletes_its_tasks(client, setup):
    owner, _, board, todo, *_ = setup
    await add(client, owner, todo, 'A')

    await client.delete(f'/columns/{todo}', headers=auth(owner))

    assert 'To do' not in await titles(client, board, owner)
