import httpx
from fastapi import Depends, HTTPException
from starlette import status

from app.db.models import User
from app.db.repositories import UserRepository
from app.deps import get_user_repository
from app.security import oauth2_scheme, verify_password

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)


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


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    user_repository: UserRepository = Depends(get_user_repository),
) -> User:
    response = httpx.get(
        "http://auth:8080/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    user = await user_repository.get_user_by_username(username=response.json()["username"])
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
