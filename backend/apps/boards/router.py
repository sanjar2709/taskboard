from fastapi import APIRouter, HTTPException, status

from apps.users.dependencies import CurrentUser
from core.db import DBSession

from . import services
from .dependencies import BoardColumn, MemberBoard, OwnBoard
from .schemas import (
    BoardCreate,
    BoardListItem,
    BoardRead,
    BoardUpdate,
    ColumnCreate,
    ColumnMove,
    ColumnRead,
    ColumnUpdate,
    MemberAdd,
    MemberRead,
)

router = APIRouter(tags=['boards'])


def bad_request(error: Exception):
    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(error))


# Boards

@router.get('/boards', response_model=list[BoardListItem])
async def list_boards(db: DBSession, user: CurrentUser):
    return await services.list_boards(db, user)


@router.post('/boards', response_model=BoardRead, status_code=status.HTTP_201_CREATED)
async def create_board(data: BoardCreate, db: DBSession, user: CurrentUser):
    return await services.create_board(db, user, data.title)


@router.get('/boards/{board_id}', response_model=BoardRead)
async def get_board(board: MemberBoard):
    return board


@router.patch('/boards/{board_id}', response_model=BoardRead)
async def update_board(data: BoardUpdate, board: OwnBoard, db: DBSession):
    board.title = data.title
    await db.commit()
    await db.refresh(board)
    return board


@router.delete('/boards/{board_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(board: OwnBoard, db: DBSession):
    await db.delete(board)
    await db.commit()


# Members

@router.post('/boards/{board_id}/members', response_model=MemberRead, status_code=status.HTTP_201_CREATED)
async def add_member(data: MemberAdd, board: OwnBoard, db: DBSession):
    try:
        return await services.add_member(db, board, data.email)
    except services.BoardError as e:
        raise bad_request(e) from None


@router.delete('/boards/{board_id}/members/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(user_id: int, board: OwnBoard, db: DBSession):
    try:
        await services.remove_member(db, board, user_id)
    except services.BoardError as e:
        raise bad_request(e) from None


# Columns

@router.post('/boards/{board_id}/columns', response_model=ColumnRead, status_code=status.HTTP_201_CREATED)
async def add_column(data: ColumnCreate, board: MemberBoard, db: DBSession):
    return await services.add_column(db, board, data.title)


@router.patch('/columns/{column_id}', response_model=ColumnRead)
async def update_column(data: ColumnUpdate, column: BoardColumn, db: DBSession):
    column.title = data.title
    await db.commit()
    await db.refresh(column)
    return column


@router.post('/columns/{column_id}/move', response_model=ColumnRead)
async def move_column(data: ColumnMove, column: BoardColumn, db: DBSession):
    return await services.move_column(db, column, data.index)


@router.delete('/columns/{column_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_column(column: BoardColumn, db: DBSession):
    await db.delete(column)
    await db.commit()
