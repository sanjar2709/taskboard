from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

from apps.boards.schemas import MemberUser


class TaskCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ''
    assignee_id: int | None = None
    due_date: date | None = None


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    assignee_id: int | None = None
    due_date: date | None = None


class TaskMove(BaseModel):
    column_id: int
    index: int = Field(ge=0, description='New place in the target column, counting from 0')


class TaskRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    board_id: int
    column_id: int
    title: str
    description: str
    position: float
    assignee: MemberUser | None
    due_date: date | None
    created_at: datetime
    updated_at: datetime
