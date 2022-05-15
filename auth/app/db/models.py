import enum
import uuid
from datetime import datetime

from app.db.session import Base
from fastapi_utils.guid_type import GUID
from sqlalchemy import Boolean, Column, DateTime, Enum, Integer, String


class Role(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    ACCOUNTANT = "accountant"
    DEVELOPER = "developer"


class User(Base):
    id = Column(Integer, primary_key=True)
    public_id = Column(
        GUID, unique=True, nullable=False, default=uuid.uuid4, index=True
    )
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    role = Column(Enum(Role), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.now)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.now, onupdate=datetime.now
    )
