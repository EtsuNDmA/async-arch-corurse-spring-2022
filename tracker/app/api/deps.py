from aiokafka import AIOKafkaProducer
from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from starlette import status
from starlette.requests import Request

from app.api.schemas import TokenData
from app.db.models import User
from app.db.repositories import TaskRepository, UserRepository
from app.db.session import Database
from app.security import oauth2_scheme
from app.settings.config import settings


def get_database(request: Request) -> Database:
    return request.app.state.db


def get_user_repository(db: Database = Depends(get_database, use_cache=True)) -> UserRepository:
    return UserRepository(db=db)


def get_task_repository(db: Database = Depends(get_database, use_cache=True)) -> TaskRepository:
    return TaskRepository(db=db)


def get_kafka_producer(request: Request) -> AIOKafkaProducer:
    return request.app.state.producer


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repository: UserRepository = Depends(get_user_repository),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError as exc:
        raise credentials_exception

    user = await user_repository.get_user_by_username(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user
