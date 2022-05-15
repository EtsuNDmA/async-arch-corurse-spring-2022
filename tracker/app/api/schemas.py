import re
from typing import Optional
from uuid import UUID

from app.db.models import TaskStatus
from loguru import logger
from pydantic import BaseModel, ValidationError, validator


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
    jira_id: Optional[str]

    @validator("description")
    def description_does_not_contain_jira_id(cls, description: str) -> str:
        description = description.strip()
        if re.match(r"^\[.*\]", description):
            logger.warning("Jira ID is not allowed in description")
            raise ValidationError
        return description

    @validator("jira_id")
    def strip_jira_id(cls, jira_id: str) -> str:
        jira_id = jira_id.strip()
        if re.match(r"^\[.*\]$", jira_id):
            logger.warning("Jira ID should not be enclosed in square brackets")
            raise ValidationError
        return jira_id


class TaskRead(BaseModel):
    id: int
    public_id: UUID
    description: str
    status: TaskStatus
    assignee: UserRead
    jira_id: Optional[str]

    class Config:
        orm_mode = True
