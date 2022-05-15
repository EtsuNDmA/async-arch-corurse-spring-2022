from uuid import UUID

from pydantic import BaseModel

from app.db.models import TaskStatus
from app.events.base import Event, EventMeta


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
    meta = EventMeta(version=1, name="task.created")
    data: TaskStream


class TaskUpdated(TaskEvent):
    meta = EventMeta(version=1, name="task.updated")
    data: TaskStream


# =====================================================================================================================
class TaskAssignedData(BaseModel):
    public_id: UUID
    assignee_id: UUID

    class Config:
        orm_mode = True


class TaskAssigned(TaskEvent):
    meta = EventMeta(version=1, name="task.assigned")
    data: TaskAssignedData


# ---------------------------------------------------------------------------------------------------------------------
class TaskCompletedData(BaseModel):
    public_id: UUID
    assignee_id: UUID

    class Config:
        orm_mode = True


class TaskCompleted(TaskEvent):
    meta = EventMeta(version=1, name="task.completed")
    data: TaskCompletedData
