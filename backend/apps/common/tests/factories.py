from itertools import count

from apps.boards.models import Board
from apps.boards.services import add_member, create_board
from apps.users.models import User
from core.db import SessionLocal
from core.security import create_access_token, hash_password

PASSWORD = 'Str0ngPass!42'

_numbers = count(1)


async def create_user(**kwargs) -> User:
    async with SessionLocal() as db:
        user = User(
            email=kwargs.pop('email', f'user{next(_numbers)}@example.com'),
            hashed_password=hash_password(PASSWORD),
            **kwargs,
        )
        db.add(user)
        await db.commit()
        return user


def auth(user: User) -> dict:
    return {'Authorization': f'Bearer {create_access_token(user.id)}'}


async def create_board_with(owner: User, *members: User, title='Board') -> Board:
    """A board with the default columns: To do, In progress, Done."""
    async with SessionLocal() as db:
        board = await create_board(db, owner, title)
        for member in members:
            await add_member(db, board, member.email)
        await db.refresh(board)
        return board
