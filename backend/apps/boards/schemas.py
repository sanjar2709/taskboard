from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from .models import MemberRole


class BoardCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)


class BoardUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=100)


class MemberUser(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    full_name: str


class MemberRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user: MemberUser
    role: MemberRole
    joined_at: datetime


class MemberAdd(BaseModel):
    email: EmailStr


class ColumnCreate(BaseModel):
    title: str = Field(min_length=1, max_length=100)


class ColumnUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=100)


class ColumnMove(BaseModel):
    index: int = Field(ge=0, description='New place of the column, counting from 0')


class ColumnRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    board_id: int
    title: str
    position: float


class BoardListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    owner_id: int
    created_at: datetime


class BoardRead(BoardListItem):
    members: list[MemberRead]
    columns: list[ColumnRead]


class ColumnWithTasks(ColumnRead):
    tasks: list['TaskRead']


class BoardDetail(BoardListItem):
    members: list[MemberRead]
    columns: list[ColumnWithTasks]


from apps.tasks.schemas import TaskRead  # noqa: E402  (circular: tasks schemas use MemberUser)

ColumnWithTasks.model_rebuild()
BoardDetail.model_rebuild()
