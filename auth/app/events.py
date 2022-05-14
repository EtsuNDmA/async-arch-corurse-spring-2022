from typing import Any
from uuid import UUID

from aiokafka import AIOKafkaProducer
from loguru import logger
from pydantic import BaseModel, Field, EmailStr


class EventMeta(BaseModel):
    version: int = 1
    name: str


class Event(BaseModel):
    _meta: EventMeta = Field(exclude=True)
    data: Any

    @property
    def key(self) -> None:
        return None

    async def send(self, kafka_producer: AIOKafkaProducer, topic: str) -> None:
        kwargs = dict(
            topic=topic,
            value=self.json().encode(),
            key=str(self.key).encode(),
            headers=[
                ("event_version", str(self._meta.version).encode()),
                ("event_name", self._meta.name.encode()),
            ]
        )
        logger.debug("Send event {}", kwargs)
        await kafka_producer.send(**kwargs)


class UserEvent(Event):
    @property
    def key(self):
        return self.data.public_id


# =====================================================================================================================
class UserStream(BaseModel):
    public_id: UUID
    username: str
    is_active: bool
    email: EmailStr
    role: str

    class Config:
        orm_mode = True


class UserCreated(UserEvent):
    _meta = EventMeta(version=1, name="UserCreated")
    data: UserStream


class UserUpdated(UserEvent):
    _meta = EventMeta(version=1, name="UserUpdated")
    data: UserStream
