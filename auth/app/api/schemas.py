import inspect
from typing import Type
from uuid import UUID

from app.db.models import Role
from fastapi import Form
from pydantic import BaseModel, EmailStr
from pydantic.fields import ModelField


def as_form(cls: Type[BaseModel]):
    new_parameters = []

    for field_name, model_field in cls.__fields__.items():
        model_field: ModelField

        new_parameters.append(
            inspect.Parameter(
                model_field.alias,
                inspect.Parameter.POSITIONAL_ONLY,
                default=Form(...)
                if not model_field.required
                else Form(model_field.default),
                annotation=model_field.outer_type_,
            )
        )

    async def as_form_func(**data):
        return cls(**data)

    sig = inspect.signature(as_form_func)
    sig = sig.replace(parameters=new_parameters)
    as_form_func.__signature__ = sig  # type: ignore
    setattr(cls, "as_form", as_form_func)
    return cls


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


@as_form
class UserWrite(BaseModel):
    username: str
    password: str
    email: EmailStr
    role: str = Role.ADMIN


class UserRead(BaseModel):
    public_id: UUID
    username: str
    is_active: bool
    email: EmailStr
    role: str

    class Config:
        orm_mode = True
