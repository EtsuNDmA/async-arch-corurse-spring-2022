from fastapi import Depends
from starlette.requests import Request

from app.db.repositories import TaskRepository, UserRepository
from app.db.session import Database


def get_database(request: Request) -> Database:
    return request.app.state.db


def get_user_repository(db: Database = Depends(get_database, use_cache=True)) -> UserRepository:
    return UserRepository(db=db)


def get_task_repository(db: Database = Depends(get_database, use_cache=True)) -> TaskRepository:
    return TaskRepository(db=db)
