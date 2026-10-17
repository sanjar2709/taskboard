from typing import Annotated

from fastapi import Depends, HTTPException, status

from apps.users.dependencies import CurrentUser
from core.db import DBSession

from .models import Board, Column, MemberRole


def check_member(board: Board | None, user_id: int, owner_only=False) -> Board:
    member = next((m for m in board.members if m.user_id == user_id), None) if board else None
    # A board you are not a member of looks the same as a board that doesn't exist
    if member is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Board not found')
    if owner_only and member.role != MemberRole.OWNER:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Only the board owner can do this')
    return board


async def get_board(board_id: int, db: DBSession, user: CurrentUser) -> Board:
    return check_member(await db.get(Board, board_id), user.id)


async def get_own_board(board_id: int, db: DBSession, user: CurrentUser) -> Board:
    return check_member(await db.get(Board, board_id), user.id, owner_only=True)


async def get_column(column_id: int, db: DBSession, user: CurrentUser) -> Column:
    column = await db.get(Column, column_id)
    if column is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Column not found')
    check_member(await db.get(Board, column.board_id), user.id)
    return column


MemberBoard = Annotated[Board, Depends(get_board)]
OwnBoard = Annotated[Board, Depends(get_own_board)]
BoardColumn = Annotated[Column, Depends(get_column)]
