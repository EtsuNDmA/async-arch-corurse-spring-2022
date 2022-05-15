from uuid import UUID

from pydantic import BaseModel

from app.db.models import TaskStatus


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserWrite(BaseModel):
    public_id: UUID
    username: str
    is_active: bool
    role: str


class UserRead(BaseModel):
    public_id: UUID
    username: str
    is_active: bool
    role: str

    class Config:
        orm_mode = True


class TaskWrite(BaseModel):
    description: str
    status: TaskStatus = TaskStatus.IN_PROGRESS


class TaskRead(BaseModel):
    id: int
    public_id: UUID
    description: str
    status: TaskStatus
    assignee: UserRead

    class Config:
        orm_mode = True
