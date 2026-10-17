from apps.common.tests.factories import auth, create_board_with, create_user


async def test_new_board_has_default_columns(client):
    user = await create_user()

    response = await client.post('/boards', json={'title': 'Portfolio'}, headers=auth(user))

    assert response.status_code == 201
    assert [c['title'] for c in response.json()['columns']] == ['To do', 'In progress', 'Done']
    assert response.json()['members'][0]['role'] == 'owner'


async def test_only_members_see_a_board(client):
    owner, member, stranger = await create_user(), await create_user(), await create_user()
    board = await create_board_with(owner, member)

    assert (await client.get(f'/boards/{board.id}', headers=auth(member))).status_code == 200
    assert (await client.get(f'/boards/{board.id}', headers=auth(stranger))).status_code == 404
    assert len((await client.get('/boards', headers=auth(member))).json()) == 1
    assert (await client.get('/boards', headers=auth(stranger))).json() == []


async def test_owner_only_actions(client):
    owner, member = await create_user(), await create_user()
    board = await create_board_with(owner, member)

    assert (await client.patch(f'/boards/{board.id}', json={'title': 'New'}, headers=auth(member))).status_code == 403
    assert (await client.delete(f'/boards/{board.id}', headers=auth(member))).status_code == 403
    response = await client.patch(f'/boards/{board.id}', json={'title': 'New'}, headers=auth(owner))
    assert response.json()['title'] == 'New'
    assert (await client.delete(f'/boards/{board.id}', headers=auth(owner))).status_code == 204


async def test_members(client):
    owner, friend = await create_user(), await create_user(email='friend@example.com')
    board = await create_board_with(owner)
    url = f'/boards/{board.id}/members'

    assert (await client.post(url, json={'email': 'friend@example.com'}, headers=auth(owner))).status_code == 201
    assert (await client.post(url, json={'email': 'friend@example.com'}, headers=auth(owner))).status_code == 400
    assert (await client.post(url, json={'email': 'nobody@example.com'}, headers=auth(owner))).status_code == 400

    assert (await client.delete(f'{url}/{owner.id}', headers=auth(owner))).status_code == 400
    assert (await client.delete(f'{url}/{friend.id}', headers=auth(owner))).status_code == 204
    assert (await client.get(f'/boards/{board.id}', headers=auth(friend))).status_code == 404


async def test_columns(client):
    owner = await create_user()
    board = await create_board_with(owner)

    review = (await client.post(f'/boards/{board.id}/columns', json={'title': 'Review'}, headers=auth(owner))).json()
    await client.post(f'/columns/{review["id"]}/move', json={'index': 1}, headers=auth(owner))
    await client.patch(f'/columns/{review["id"]}', json={'title': 'Code review'}, headers=auth(owner))

    columns = (await client.get(f'/boards/{board.id}', headers=auth(owner))).json()['columns']
    assert [c['title'] for c in columns] == ['To do', 'Code review', 'In progress', 'Done']

    assert (await client.delete(f'/columns/{review["id"]}', headers=auth(owner))).status_code == 204


async def test_repeated_moves_into_one_gap_keep_order(client):
    owner = await create_user()
    board = await create_board_with(owner)
    first, second, third = (c.id for c in board.columns)

    # Squeezing columns into the same gap again and again forces a renumbering at some point
    for i in range(60):
        column = second if i % 2 == 0 else third
        await client.post(f'/columns/{column}/move', json={'index': 1}, headers=auth(owner))

    columns = (await client.get(f'/boards/{board.id}', headers=auth(owner))).json()['columns']
    assert [c['id'] for c in columns] == [first, third, second]
    assert len({c['position'] for c in columns}) == 3


async def test_column_of_foreign_board(client):
    owner, stranger = await create_user(), await create_user()
    board = await create_board_with(owner)

    response = await client.patch(f'/columns/{board.columns[0].id}', json={'title': 'x'}, headers=auth(stranger))

    assert response.status_code == 404
