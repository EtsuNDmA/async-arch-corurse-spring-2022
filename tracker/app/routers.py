from fastapi import APIRouter, Depends, HTTPException
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.templating import Jinja2Templates, _TemplateResponse

from app.db.models import User
from app.db.repositories import TaskRepository, UserRepository
from app.deps import get_task_repository, get_user_repository
from app.schemas import TaskRead, TaskWrite, UserRead
from app.services import get_current_active_user, get_current_user

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
    return templates.TemplateResponse("login.html", context=context)


@router.get("/users/me", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user


@router.post("/tasks", response_model=TaskRead)
async def create_task(
    task_to_create: TaskWrite,
    task_repository: TaskRepository = Depends(get_task_repository),
    user_repository: UserRepository = Depends(get_user_repository),
):
    return await task_repository.create_new_task(
        task_to_create,
    )


@router.get("/tasks", response_model=TaskRead)
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
