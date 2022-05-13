import httpx
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse, Response
from starlette.templating import Jinja2Templates, _TemplateResponse

from app.api.deps import get_current_active_user, get_task_repository
from app.api.schemas import TaskRead, TaskWrite, UserRead
from app.db.models import Role, Task, User
from app.db.repositories import TaskRepository
from app.settings.config import settings

router = APIRouter()

templates = Jinja2Templates(directory="app/api/templates")

CAN_SHUFFLE_TASKS = (Role.ADMIN, Role.MANAGER)
CAN_ADD_TASKS = (Role.ADMIN, Role.MANAGER, Role.ACCOUNTANT, Role.MANAGER)
CAN_VIEW_TASKS = (Role.ADMIN, Role.MANAGER, Role.ACCOUNTANT, Role.MANAGER)


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
    context = {"request": request, "oauth_token_url": settings.OAUTH_TOKEN_URL}
    return templates.TemplateResponse("login.html", context=context)


@router.get(
    "/tasks",
    response_class=HTMLResponse,
    description="Get all tasks",
    name="tasks-list",
)
def get_all_tasks(
    request: Request,
) -> _TemplateResponse:
    context = {
        "request": request,
    }
    return templates.TemplateResponse("tasks.html", context=context)


@router.get(
    "/tasks/my",
    response_class=HTMLResponse,
    description="Get current user tasks",
    name="tasks-my",
)
def get_current_user(
    request: Request,
) -> _TemplateResponse:
    context = {
        "request": request,
    }
    return templates.TemplateResponse("tasks_my.html", context=context)


@router.post(
    "/api/token",
    description="Get auth token",
    name="token",
)
async def get_auth_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            settings.OAUTH_TOKEN_URL, data={"username": form_data.username, "password": form_data.password}
        )
    response = Response(
        content=response.content,
        media_type="application/json",
        status_code=response.status_code,
    )
    return response


@router.get(
    "/api/tasks",
    description="Get all tasks",
    name="tasks-list",
    response_model=list[TaskRead],
)
async def read_all_tasks(
    task_repository: TaskRepository = Depends(get_task_repository),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role not in CAN_VIEW_TASKS:
        raise HTTPException(status_code=403, detail="Forbidden")
    tasks = await task_repository.get_all_tasks()
    return tasks


@router.post(
    "/api/tasks",
    description="Register new task",
    name="create-task",
    response_model=TaskRead,
    status_code=201,
)
async def create_task(
    task_to_create: TaskWrite,
    task_repository: TaskRepository = Depends(get_task_repository),
    current_user: User = Depends(get_current_active_user),
) -> Task:
    if current_user.role not in CAN_ADD_TASKS:
        raise HTTPException(status_code=403, detail="Forbidden")
    new_task: Task = await task_repository.create_task(task_to_create)
    return new_task


@router.post(
    "/api/tasks/shuffle",
    description="Shuffle tasks",
    name="shuffle-task",
)
async def shuffle_task(
    task_repository: TaskRepository = Depends(get_task_repository),
    current_user: User = Depends(get_current_active_user),
) -> Task:
    if current_user.role not in CAN_SHUFFLE_TASKS:
        raise HTTPException(status_code=403, detail="Forbidden")

    new_task: Task = await task_repository.shuffle_tasks()
    return new_task


@router.get("/api/tasks/my", response_model=UserRead)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user
