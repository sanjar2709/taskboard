from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.boards.models import Board, Column
from apps.common.ordering import neighbours, position_between, renumbered
from apps.users.models import User

from .models import Task
from .schemas import TaskCreate, TaskUpdate


class TaskError(Exception):
    """Business rule violation. The message is safe to show to the client."""


def check_assignee(board: Board, assignee_id: int | None):
    if assignee_id is not None and not any(m.user_id == assignee_id for m in board.members):
        raise TaskError('Tasks can be assigned only to board members')


async def create_task(db: AsyncSession, board: Board, column: Column, user: User, data: TaskCreate) -> Task:
    check_assignee(board, data.assignee_id)
    last = await db.scalar(select(func.max(Task.position)).where(Task.column_id == column.id))
    task = Task(
        **data.model_dump(),
        board_id=board.id,
        column_id=column.id,
        position=position_between(last, None),
        created_by_id=user.id,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def update_task(db: AsyncSession, board: Board, task: Task, data: TaskUpdate) -> Task:
    changes = data.model_dump(exclude_unset=True)
    if 'assignee_id' in changes:
        check_assignee(board, changes['assignee_id'])
    for field, value in changes.items():
        setattr(task, field, value)
    await db.commit()
    await db.refresh(task)
    return task


async def move_task(db: AsyncSession, task: Task, column: Column, index: int) -> Task:
    if column.board_id != task.board_id:
        raise TaskError('Tasks can be moved only inside their board')

    others = list(await db.scalars(
        select(Task).where(Task.column_id == column.id, Task.id != task.id).order_by(Task.position)
    ))
    task.column_id = column.id
    position = position_between(*neighbours([t.position for t in others], index))
    if position is None:
        # Gap is too small, renumber this column once
        ordered = others[:index] + [task] + others[index:]
        for item, new_position in zip(ordered, renumbered(len(ordered)), strict=True):
            item.position = new_position
    else:
        task.position = position
    await db.commit()
    await db.refresh(task)
    return task
