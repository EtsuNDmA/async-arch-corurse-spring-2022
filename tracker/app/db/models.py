import enum
import uuid
from datetime import datetime

from fastapi_utils.guid_type import GUID
from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from app.db.session import Base


class Role(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    ACCOUNTANT = "accountant"
    DEVELOPER = "developer"


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(GUID, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False, index=True)
    is_active = Column(Boolean(), default=True)
    role = Column(Enum(Role), nullable=False)


class TaskStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Task(Base):
    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(GUID, default=uuid.uuid4)
    description = Column(String, nullable=False)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.IN_PROGRESS)
    assignee_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    assignee = relationship("User")
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(DateTime(timezone=True), default=datetime.now, onupdate=datetime.now)
