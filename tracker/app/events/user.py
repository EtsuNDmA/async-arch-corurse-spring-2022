from uuid import UUID

from pydantic import BaseModel

from app.events.base import Event, EventMeta


class UserStream(BaseModel):
    public_id: UUID
    username: str
    is_active: bool
    role: str

    class Config:
        orm_mode = True


class UserCreated(Event):
    meta = EventMeta(version=1, name="user.created")
    data: UserStream


class UserUpdated(Event):
    meta = EventMeta(version=1, name="user.updated")
    data: UserStream
