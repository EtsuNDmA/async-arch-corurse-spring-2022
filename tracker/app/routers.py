from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette import status
from starlette.requests import Request
from starlette.responses import RedirectResponse, HTMLResponse
from starlette.templating import Jinja2Templates, _TemplateResponse

from app.db.models import User
from app.db.repositories import UserRepository
from app.deps import get_user_repository
from app.schemas import Role

from app.schemas import UserRead
from app.services import get_current_active_user

ACCESS_TOKEN_EXPIRE_MINUTES = 60

router = APIRouter()


templates = Jinja2Templates(directory="app/templates")


@router.get("/")
async def redirect_to_dashboard() -> RedirectResponse:
    return RedirectResponse("/dashboard", status_code=302)


@router.get(
    "/dashboard",
    response_class=HTMLResponse,
    description="Dashboard",
    name="dashboard",
)
def dashboard(request: Request) -> _TemplateResponse:
    context = {"request": request}
    return templates.TemplateResponse("dashboard.html", context=context)


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
