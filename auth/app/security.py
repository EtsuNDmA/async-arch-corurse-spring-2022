from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
hasher = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return hasher.verify(plain_password, hashed_password)


def get_password_hash(password) -> str:
    return hasher.hash(password)
