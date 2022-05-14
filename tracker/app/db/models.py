import enum
import uuid
from datetime import datetime

from app.db.session import Base
from fastapi_utils.guid_type import GUID
from sqlalchemy import (Boolean, Column, DateTime, Enum, ForeignKey, Integer,
                        String)
from sqlalchemy.orm import relationship


class Role(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    ACCOUNTANT = "accountant"
    DEVELOPER = "developer"


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(GUID, unique=True, nullable=False, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    is_active = Column(Boolean(), default=True)
    role = Column(Enum(Role), nullable=False)

    def __repr__(self):
        return f'User(username={self.username}, role={self.role})'


class TaskStatus(str, enum.Enum):
    IN_PROGRESS = "in_progress"
    DONE = "done"


class Task(Base):
    id = Column(Integer, primary_key=True, index=True)
    public_id = Column(GUID, unique=True, nullable=False, default=uuid.uuid4)
    description = Column(String, nullable=False)
    status = Column(Enum(TaskStatus), nullable=False, default=TaskStatus.IN_PROGRESS)
    assignee_id = Column(GUID, ForeignKey("user.public_id"), nullable=False)
    assignee = relationship("User")
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.now, onupdate=datetime.now
    )

    def __repr__(self):
        return f'Task(description={self.description}, status={self.status})'
