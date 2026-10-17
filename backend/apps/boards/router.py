from fastapi import APIRouter, HTTPException, status

from apps.users.dependencies import CurrentUser
from core.db import DBSession
from core.realtime import broadcaster

from . import services
from .dependencies import BoardColumn, MemberBoard, OwnBoard
from .schemas import (
    BoardCreate,
    BoardDetail,
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


def dump(schema, obj) -> dict:
    return schema.model_validate(obj).model_dump(mode='json')


# Boards

@router.get('/boards', response_model=list[BoardListItem])
async def list_boards(db: DBSession, user: CurrentUser):
    return await services.list_boards(db, user)


@router.post('/boards', response_model=BoardRead, status_code=status.HTTP_201_CREATED)
async def create_board(data: BoardCreate, db: DBSession, user: CurrentUser):
    return await services.create_board(db, user, data.title)


@router.get('/boards/{board_id}', response_model=BoardDetail)
async def get_board(board: MemberBoard):
    return board


@router.patch('/boards/{board_id}', response_model=BoardRead)
async def update_board(data: BoardUpdate, board: OwnBoard, db: DBSession, user: CurrentUser):
    board.title = data.title
    await db.commit()
    await db.refresh(board)
    await broadcaster.publish(board.id, 'board.updated', {'id': board.id, 'title': board.title}, user.id)
    return board


@router.delete('/boards/{board_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_board(board: OwnBoard, db: DBSession, user: CurrentUser):
    board_id = board.id
    await db.delete(board)
    await db.commit()
    await broadcaster.publish(board_id, 'board.deleted', {'id': board_id}, user.id)


# Members

@router.post('/boards/{board_id}/members', response_model=MemberRead, status_code=status.HTTP_201_CREATED)
async def add_member(data: MemberAdd, board: OwnBoard, db: DBSession, user: CurrentUser):
    try:
        member = await services.add_member(db, board, data.email)
    except services.BoardError as e:
        raise bad_request(e) from None
    await broadcaster.publish(board.id, 'member.added', dump(MemberRead, member), user.id)
    return member


@router.delete('/boards/{board_id}/members/{user_id}', status_code=status.HTTP_204_NO_CONTENT)
async def remove_member(user_id: int, board: OwnBoard, db: DBSession, user: CurrentUser):
    try:
        await services.remove_member(db, board, user_id)
    except services.BoardError as e:
        raise bad_request(e) from None
    await broadcaster.publish(board.id, 'member.removed', {'user_id': user_id}, user.id)


# Columns

@router.post('/boards/{board_id}/columns', response_model=ColumnRead, status_code=status.HTTP_201_CREATED)
async def add_column(data: ColumnCreate, board: MemberBoard, db: DBSession, user: CurrentUser):
    column = await services.add_column(db, board, data.title)
    await broadcaster.publish(board.id, 'column.created', dump(ColumnRead, column), user.id)
    return column


@router.patch('/columns/{column_id}', response_model=ColumnRead)
async def update_column(data: ColumnUpdate, column: BoardColumn, db: DBSession, user: CurrentUser):
    column.title = data.title
    await db.commit()
    await db.refresh(column)
    await broadcaster.publish(column.board_id, 'column.updated', dump(ColumnRead, column), user.id)
    return column


@router.post('/columns/{column_id}/move', response_model=ColumnRead)
async def move_column(data: ColumnMove, column: BoardColumn, db: DBSession, user: CurrentUser):
    column = await services.move_column(db, column, data.index)
    data = {**dump(ColumnRead, column), 'index': data.index}
    await broadcaster.publish(column.board_id, 'column.moved', data, user.id)
    return column


@router.delete('/columns/{column_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_column(column: BoardColumn, db: DBSession, user: CurrentUser):
    board_id, column_id = column.board_id, column.id
    await db.delete(column)
    await db.commit()
    await broadcaster.publish(board_id, 'column.deleted', {'id': column_id}, user.id)
