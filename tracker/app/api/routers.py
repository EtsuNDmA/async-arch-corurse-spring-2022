import httpx
from aiokafka import AIOKafkaProducer
from app.api.deps import (get_current_active_user, get_kafka_producer,
                          get_task_repository)
from app.api.schemas import TaskRead, TaskWrite
from app.db.models import Role, Task, User
from app.db.repositories import TaskRepository
from app.events import Event, TaskUpdated, TaskCreated, TaskAssigned, TaskAssignedData, TaskCompleted, \
    TaskCompletedData, TaskStream
from app.settings.config import settings
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse, Response
from starlette.templating import Jinja2Templates, _TemplateResponse

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
            settings.OAUTH_TOKEN_URL,
            data={"username": form_data.username, "password": form_data.password},
        )
    response = Response(
        content=response.content,
        media_type="application/json",
        status_code=response.status_code,
    )
    return response


@router.get("/api/tasks", response_model=list[TaskRead])
async def read_all_tasks(
    task_repository: TaskRepository = Depends(get_task_repository),
    current_user: User = Depends(get_current_active_user),
):
    if current_user.role not in CAN_VIEW_TASKS:
        raise HTTPException(status_code=403, detail="Forbidden")
    return await task_repository.get_all_tasks()


@router.get("/api/tasks/my", response_model=list[TaskRead])
async def read_tasks_my(
    task_repository: TaskRepository = Depends(get_task_repository),
    current_user: User = Depends(get_current_active_user),
):
    return await task_repository.get_tasks_assigned_to_user(current_user.public_id)


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
    kafka_producer: AIOKafkaProducer = Depends(get_kafka_producer),
) -> Task:
    if current_user.role not in CAN_ADD_TASKS:
        raise HTTPException(status_code=403, detail="Forbidden")
    new_task: Task = await task_repository.create_task(task_to_create)

    event = TaskCreated(data=TaskStream.from_orm(new_task))
    await event.send(kafka_producer, topic=settings.KAFKA_TASK_STREAMING_TOPIC)

    event = TaskAssigned(data=TaskAssignedData.from_orm(new_task))
    await event.send(kafka_producer, topic=settings.KAFKA_TASK_LIFECYCLE_TOPIC)

    return new_task


@router.post(
    "/api/tasks/{task_id}/complete",
    description="Update task",
    name="update-task",
    response_model=TaskRead,
)
async def complete_task(
    task_id: int,
    task_repository: TaskRepository = Depends(get_task_repository),
    current_user: User = Depends(get_current_active_user),
    kafka_producer: AIOKafkaProducer = Depends(get_kafka_producer),
) -> Task:
    task = await task_repository.complete_task(task_id, current_user)

    event = TaskUpdated(data=TaskStream.from_orm(task))
    await event.send(kafka_producer, topic=settings.KAFKA_TASK_STREAMING_TOPIC)

    event = TaskCompleted(data=TaskCompletedData.from_orm(task))
    await event.send(kafka_producer, topic=settings.KAFKA_TASK_LIFECYCLE_TOPIC)

    return task


@router.post(
    "/api/tasks/shuffle",
    description="Shuffle tasks",
    name="shuffle-task",
)
async def shuffle_task(
    task_repository: TaskRepository = Depends(get_task_repository),
    current_user: User = Depends(get_current_active_user),
    kafka_producer: AIOKafkaProducer = Depends(get_kafka_producer),
) -> None:
    if current_user.role not in CAN_SHUFFLE_TASKS:
        raise HTTPException(status_code=403, detail="Forbidden")

    updated_tasks: Task = await task_repository.shuffle_tasks()

    for task in updated_tasks:
        event = TaskUpdated(data=TaskStream.from_orm(task))
        await event.send(kafka_producer, topic=settings.KAFKA_TASK_STREAMING_TOPIC)

        event = TaskAssigned(data=TaskAssignedData.from_orm(task))
        await event.send(kafka_producer, topic=settings.KAFKA_TASK_LIFECYCLE_TOPIC)
