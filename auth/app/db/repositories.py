from app.db.models import User
from app.schemas import UserCreate

from dataclasses import dataclass

from sqlalchemy import select

from app.db.session import Database


@dataclass
class UserRepository:
    db: Database

    async def get_user_by_id(self, user_id: int) -> User | None:
        query = select(User).filter_by(id=user_id)
        async with self.db.session() as session:
            user = await session.execute(query)
            return user.scalar()

    async def get_user_by_username(self, username: str) -> User | None:
        query = select(User).filter_by(username=username)
        async with self.db.session() as session:
            user = await session.execute(query)
            return user.scalar()

    async def create_new_user(self, user_to_create: UserCreate) -> User:
        from app.security import get_password_hash

        user = User(
            username=user_to_create.username,
            email=user_to_create.email,
            hashed_password=get_password_hash(user_to_create.password),
            is_active=True,
            role=user_to_create.role,
        )
        async with self.db.session() as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user
