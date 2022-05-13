from datetime import datetime, timedelta

from app.db.models import User
from app.db.repositories import UserRepository
from app.settings.config import settings
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)
hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return hasher.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    return hasher.hash(password)


def create_access_token(
    data: dict, expires_delta: timedelta = timedelta(minutes=15)
) -> str:
    data_to_encode = data.copy()
    expires_at = datetime.utcnow() + expires_delta
    data_to_encode.update({"exp": expires_at})
    encoded_jwt = jwt.encode(
        data_to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


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
