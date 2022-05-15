from uuid import UUID

from pydantic import BaseModel, EmailStr

from app.events.base import Event, EventMeta


class BaseUserEvent(Event):
    @property
    def key(self):
        return self.data.public_id


class UserStream(BaseModel):
    public_id: UUID
    username: str
    is_active: bool
    email: EmailStr
    role: str

    class Config:
        orm_mode = True


class UserCreated(BaseUserEvent):
    meta = EventMeta(version=1, name="user.created")
    data: UserStream


class UserUpdated(BaseUserEvent):
    meta = EventMeta(version=1, name="user.updated")
    data: UserStream
