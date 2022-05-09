from datetime import timedelta

from fastapi import APIRouter, Depends, Form, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates, _TemplateResponse

from app.db.models import User
from app.db.repositories import UserRepository
from app.deps import get_user_repository
from app.schemas import Role, Token, UserCreate, UserRead
from app.services import (
    authenticate_user,
    create_access_token,
    get_current_active_user,
    register_user,
)
from app.settings.config import settings

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def redirect_to_dashboard() -> RedirectResponse:
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


@router.post(
    "/register",
    description="Register new user",
    name="register",
    response_model=UserRead,
    status_code=201,
)
async def register_new_user(
    user_to_create: UserCreate = Depends(UserCreate.as_form),
    user_repository: UserRepository = Depends(get_user_repository),
):
    new_user = await register_user(user_to_create, user_repository)
    return new_user


@router.post(
    "/token",
    description="Get auth token",
    name="token",
    response_model=Token,
)
async def get_auth_token(
    form_data: OAuth2PasswordRequestForm = Depends(), user_repository: UserRepository = Depends(get_user_repository)
):
    user = await authenticate_user(form_data.username, form_data.password, user_repository)
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


@router.post(
    "/users",
    description="Register new user",
    name="register",
    response_model=UserRead,
    status_code=201,
)
async def add_user(
    user_to_create: UserCreate,
    user_repository: UserRepository = Depends(get_user_repository),
):
    new_user = await register_user(user_to_create, user_repository)
    return new_user


@router.get("/users/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get("/users/{user_id}", response_model=UserRead)
async def read_users_by_id(
    user_id: int,
    current_user: User = Depends(get_current_active_user),
    user_repository: UserRepository = Depends(get_user_repository),
):
    if not current_user.role == Role.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")

    user = user_repository.get_user_by_id(user_id)

    return user
