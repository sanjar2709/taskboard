from fastapi import APIRouter, HTTPException, status

from apps.boards.dependencies import BoardColumn, check_member
from apps.boards.models import Board, Column
from apps.users.dependencies import CurrentUser
from core.db import DBSession
from core.realtime import broadcaster

from . import services
from .models import Task
from .schemas import TaskCreate, TaskMove, TaskRead, TaskUpdate

router = APIRouter(tags=['tasks'])


async def publish(event: str, task: Task, user, **extra):
    data = {**TaskRead.model_validate(task).model_dump(mode='json'), **extra}
    await broadcaster.publish(task.board_id, event, data, user.id)


async def get_task_and_board(task_id: int, db, user) -> tuple[Task, Board]:
    task = await db.get(Task, task_id)
    if task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Task not found')
    board = check_member(await db.get(Board, task.board_id), user.id)
    return task, board


@router.post('/columns/{column_id}/tasks', response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(data: TaskCreate, column: BoardColumn, db: DBSession, user: CurrentUser):
    board = await db.get(Board, column.board_id)
    try:
        task = await services.create_task(db, board, column, user, data)
    except services.TaskError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None
    await publish('task.created', task, user)
    return task


@router.get('/tasks/{task_id}', response_model=TaskRead)
async def get_task(task_id: int, db: DBSession, user: CurrentUser):
    task, _ = await get_task_and_board(task_id, db, user)
    return task


@router.patch('/tasks/{task_id}', response_model=TaskRead)
async def update_task(task_id: int, data: TaskUpdate, db: DBSession, user: CurrentUser):
    task, board = await get_task_and_board(task_id, db, user)
    try:
        task = await services.update_task(db, board, task, data)
    except services.TaskError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None
    await publish('task.updated', task, user)
    return task


@router.post('/tasks/{task_id}/move', response_model=TaskRead)
async def move_task(task_id: int, data: TaskMove, db: DBSession, user: CurrentUser):
    task, _ = await get_task_and_board(task_id, db, user)
    column = await db.get(Column, data.column_id)
    if column is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Column not found')
    try:
        task = await services.move_task(db, task, column, data.index)
    except services.TaskError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)) from None
    await publish('task.moved', task, user, index=data.index)
    return task


@router.delete('/tasks/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: int, db: DBSession, user: CurrentUser):
    task, _ = await get_task_and_board(task_id, db, user)
    board_id, column_id = task.board_id, task.column_id
    await db.delete(task)
    await db.commit()
    await broadcaster.publish(board_id, 'task.deleted', {'id': task_id, 'column_id': column_id}, user.id)
