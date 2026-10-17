from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from apps.common.ordering import neighbours, position_between, renumbered
from apps.users.models import User
from apps.users.services import get_by_email

from .models import Board, BoardMember, Column, MemberRole

DEFAULT_COLUMNS = ('To do', 'In progress', 'Done')


class BoardError(Exception):
    """Business rule violation. The message is safe to show to the client."""


async def list_boards(db: AsyncSession, user: User) -> list[Board]:
    query = (
        select(Board)
        .join(BoardMember, BoardMember.board_id == Board.id)
        .where(BoardMember.user_id == user.id)
        .order_by(Board.created_at.desc())
    )
    return list(await db.scalars(query))


async def create_board(db: AsyncSession, user: User, title: str) -> Board:
    positions = renumbered(len(DEFAULT_COLUMNS))
    board = Board(
        title=title,
        owner_id=user.id,
        members=[BoardMember(user_id=user.id, role=MemberRole.OWNER)],
        columns=[Column(title=t, position=p) for t, p in zip(DEFAULT_COLUMNS, positions, strict=True)],
    )
    db.add(board)
    await db.commit()
    await db.refresh(board)
    return board


async def add_member(db: AsyncSession, board: Board, email: str) -> BoardMember:
    user = await get_by_email(db, email)
    if user is None:
        raise BoardError('No user with this email')
    if any(m.user_id == user.id for m in board.members):
        raise BoardError('This user is already a member')

    member = BoardMember(board_id=board.id, user_id=user.id, role=MemberRole.MEMBER)
    db.add(member)
    await db.commit()
    await db.refresh(board)
    return next(m for m in board.members if m.user_id == user.id)


async def remove_member(db: AsyncSession, board: Board, user_id: int):
    member = next((m for m in board.members if m.user_id == user_id), None)
    if member is None:
        raise BoardError('This user is not a member')
    if member.role == MemberRole.OWNER:
        raise BoardError('The owner cannot be removed')
    await db.delete(member)
    await db.commit()


async def add_column(db: AsyncSession, board: Board, title: str) -> Column:
    last = board.columns[-1].position if board.columns else None
    column = Column(board_id=board.id, title=title, position=position_between(last, None))
    db.add(column)
    await db.commit()
    await db.refresh(column)
    return column


async def move_column(db: AsyncSession, column: Column, index: int) -> Column:
    others = list(await db.scalars(
        select(Column).where(Column.board_id == column.board_id, Column.id != column.id).order_by(Column.position)
    ))
    position = position_between(*neighbours([c.position for c in others], index))
    if position is None:
        # Gap is too small, renumber the whole board once
        ordered = others[:index] + [column] + others[index:]
        for item, new_position in zip(ordered, renumbered(len(ordered)), strict=True):
            item.position = new_position
    else:
        column.position = position
    await db.commit()
    await db.refresh(column)
    return column
