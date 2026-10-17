# Every model has to be imported here, so Alembic can see it when generating migrations
from apps.boards.models import Board, BoardMember, Column
from apps.tasks.models import Task
from apps.users.models import User

__all__ = ('Board', 'BoardMember', 'Column', 'Task', 'User')
