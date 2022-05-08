from pydantic import BaseModel, EmailStr

from app.db.models import Role


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr
    role: str = Role.ADMIN


class UserRead(BaseModel):
    id: int
    username: str
    is_active: bool
    email: EmailStr
    role: str

    class Config:
        orm_mode = True
