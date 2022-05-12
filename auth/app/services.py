from datetime import datetime, timedelta

from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from starlette import status

from app.db.models import User
from app.db.repositories import UserRepository
from app.api.deps import get_user_repository
from app.api.schemas import Role, TokenData, UserCreate
from app.security import oauth2_scheme, verify_password
from app.settings.config import settings


async def authenticate_user(
    username: str,
    password: str,
    user_repository: UserRepository,
) -> User | None:
    user = await user_repository.get_user_by_username(username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def create_access_token(data: dict, expires_delta: timedelta = timedelta(minutes=15)) -> str:
    data_to_encode = data.copy()
    expires_at = datetime.utcnow() + expires_delta
    data_to_encode.update({"exp": expires_at})
    encoded_jwt = jwt.encode(data_to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


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
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_user_by_id(
    user_id: int,
    current_user: User = Depends(get_current_user),
    user_repository: UserRepository = Depends(get_user_repository),
):
    if not current_user.role == Role.ADMIN:
        raise HTTPException(status_code=403, detail="Forbidden")

    user = user_repository.get_user_by_id(user_id)

    return user


async def register_user(
    user_to_create: UserCreate,
    user_repository: UserRepository,
) -> User:
    return await user_repository.create_new_user(user_to_create)
