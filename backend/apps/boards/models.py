from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.common.models import TimeStampedMixin
from apps.users.models import User
from core.db import Base


class MemberRole(StrEnum):
    OWNER = 'owner'
    MEMBER = 'member'


class Board(TimeStampedMixin, Base):
    __tablename__ = 'boards'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))

    members: Mapped[list['BoardMember']] = relationship(
        back_populates='board',
        cascade='all, delete-orphan',
        lazy='selectin',
    )
    columns: Mapped[list['Column']] = relationship(
        back_populates='board',
        cascade='all, delete-orphan',
        order_by='Column.position',
        lazy='selectin',
    )

    def __repr__(self):
        return f'<Board {self.title}>'


class BoardMember(Base):
    __tablename__ = 'board_members'

    board_id: Mapped[int] = mapped_column(ForeignKey('boards.id', ondelete='CASCADE'), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), primary_key=True, index=True)
    role: Mapped[MemberRole] = mapped_column(
        Enum(MemberRole, native_enum=False, length=20, values_callable=lambda e: [m.value for m in e]),
        default=MemberRole.MEMBER,
    )
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    board: Mapped[Board] = relationship(back_populates='members')
    user: Mapped[User] = relationship(lazy='joined')


class Column(TimeStampedMixin, Base):
    __tablename__ = 'columns'

    id: Mapped[int] = mapped_column(primary_key=True)
    board_id: Mapped[int] = mapped_column(ForeignKey('boards.id', ondelete='CASCADE'), index=True)
    title: Mapped[str] = mapped_column(String(100))
    position: Mapped[float] = mapped_column(Float)

    board: Mapped[Board] = relationship(back_populates='columns')
    tasks: Mapped[list['Task']] = relationship(  # noqa: F821  (apps.tasks.models)
        order_by='Task.position',
        cascade='all, delete-orphan',
        lazy='selectin',
    )

    def __repr__(self):
        return f'<Column {self.title}>'
