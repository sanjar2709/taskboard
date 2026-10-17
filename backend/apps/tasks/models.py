from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from apps.common.models import TimeStampedMixin
from apps.users.models import User
from core.db import Base


class Task(TimeStampedMixin, Base):
    __tablename__ = 'tasks'
    __table_args__ = (
        Index('ix_tasks_column_position', 'column_id', 'position'),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    # board_id is stored next to column_id, so permission checks don't need a join
    board_id: Mapped[int] = mapped_column(ForeignKey('boards.id', ondelete='CASCADE'), index=True)
    column_id: Mapped[int] = mapped_column(ForeignKey('columns.id', ondelete='CASCADE'))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default='')
    position: Mapped[float] = mapped_column(Float)
    assignee_id: Mapped[int | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'))
    due_date: Mapped[date | None] = mapped_column(Date)
    created_by_id: Mapped[int | None] = mapped_column(ForeignKey('users.id', ondelete='SET NULL'))

    assignee: Mapped[User | None] = relationship(foreign_keys=[assignee_id], lazy='joined')

    def __repr__(self):
        return f'<Task {self.title}>'
