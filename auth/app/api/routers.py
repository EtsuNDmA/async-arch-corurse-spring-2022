from datetime import timedelta

from aiokafka import AIOKafkaProducer
from app.api.deps import (
    get_current_active_user,
    get_kafka_producer,
    get_user_repository,
)
from app.api.schemas import Role, Token, UserRead, UserWrite
from app.db.models import User
from app.db.repositories import UserRepository
from app.events.user import UserCreated, UserStream
from app.security import authenticate_user, create_access_token
from app.settings.config import settings
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates, _TemplateResponse

router = APIRouter()

templates = Jinja2Templates(directory="app/api/templates")


@router.get("/")
async def redirect_to_login() -> RedirectResponse:
    return RedirectResponse("/login", status_code=302)


@router.get(
    "/login",
    response_class=HTMLResponse,
    description="Login",
    name="login",
)
def show_login_form(request: Request) -> _TemplateResponse:
    context = {"request": request}
    return templates.TemplateResponse("login.html", context=context)


@router.get(
    "/register",
    response_class=HTMLResponse,
    description="Show registration form",
    name="register",
)
def show_registration_form(request: Request) -> _TemplateResponse:
    available_roles = [r.value for r in Role]
    context = {"request": request, "available_roles": available_roles}
    return templates.TemplateResponse("register.html", context=context)


@router.get(
    "/users",
    response_class=HTMLResponse,
    description="Get all users",
    name="users-list",
)
def get_all_users(
    request: Request,
) -> _TemplateResponse:
    context = {
        "request": request,
    }
    return templates.TemplateResponse("users.html", context=context)


@router.get(
    "/users/me",
    response_class=HTMLResponse,
    description="Get current user",
    name="users-me",
)
def get_current_user(
    request: Request,
) -> _TemplateResponse:
    context = {
        "request": request,
    }
    return templates.TemplateResponse("users_me.html", context=context)


@router.post(
    "/api/token",
    description="Get auth token",
    name="token",
    response_model=Token,
)
async def get_auth_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    user_repository: UserRepository = Depends(get_user_repository),
):
    user = await authenticate_user(
        form_data.username, form_data.password, user_repository
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/api/users",
    description="Get all users",
    name="users-list",
    response_model=list[UserRead],
)
async def read_all_users(
    user_repository: UserRepository = Depends(get_user_repository),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role != Role.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")
    users = await user_repository.get_all_users()
    return users


@router.post(
    "/api/users",
    description="Register new user",
    name="register",
    response_model=UserRead,
    status_code=201,
)
async def create_user(
    user_to_create: UserWrite,
    user_repository: UserRepository = Depends(get_user_repository),
    kafka_producer: AIOKafkaProducer = Depends(get_kafka_producer),
):
    new_user = await user_repository.create_new_user(user_to_create)

    event = UserCreated(data=UserStream.from_orm(new_user))
    await event.send(kafka_producer, topic=settings.KAFKA_USER_STREAMING_TOPIC)

    return new_user


@router.get("/api/users/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get("/api/users/{username}", response_model=UserRead)
async def read_users_by_username(
    username: str,
    current_user: User = Depends(get_current_active_user),
    user_repository: UserRepository = Depends(get_user_repository),
):
    if not current_user.role == Role.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")

    user = user_repository.get_user_by_username(username)

    return user
