from typing import Any
from uuid import UUID

from aiokafka import AIOKafkaProducer
from loguru import logger
from pydantic import BaseModel, Field

from app.db.models import TaskStatus


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


class TaskEvent(Event):
    @property
    def key(self):
        return self.data.public_id


# =====================================================================================================================
class TaskStream(BaseModel):
    public_id: UUID
    description: str
    status: TaskStatus
    assignee_id: UUID

    class Config:
        orm_mode = True


class TaskCreated(TaskEvent):
    _meta = EventMeta(version=1, name="TaskCreated")
    data: TaskStream


class TaskUpdated(TaskEvent):
    _meta = EventMeta(version=1, name="TaskUpdated")
    data: TaskStream


# =====================================================================================================================
class TaskAssignedData(BaseModel):
    public_id: UUID
    assignee_id: UUID

    class Config:
        orm_mode = True


class TaskAssigned(TaskEvent):
    _meta = EventMeta(version=1, name="TaskAssigned")
    data: TaskAssignedData


# ---------------------------------------------------------------------------------------------------------------------
class TaskCompletedData(BaseModel):
    public_id: UUID
    assignee_id: UUID

    class Config:
        orm_mode = True


class TaskCompleted(TaskEvent):
    _meta = EventMeta(version=1, name="TaskCompleted")
    data: TaskCompletedData
