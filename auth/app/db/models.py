import enum

from sqlalchemy import Boolean, Column, Integer, String, Enum

from app.db.session import Base


class Role(str, enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    ACCOUNTANT = "accountant"
    DEVELOPER = "developer"


class User(Base):
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, nullable=False, index=True)
    email = Column(String, nullable=False, unique=True, index=True)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean(), default=True)
    role = Column(Enum(Role), nullable=False)
