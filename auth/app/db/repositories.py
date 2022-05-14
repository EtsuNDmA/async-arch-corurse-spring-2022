from dataclasses import dataclass
from uuid import UUID

from app.api.schemas import UserWrite
from app.db.models import Role, User
from app.db.session import Database
from sqlalchemy import select, update


@dataclass
class UserRepository:
    db: Database

    async def get_all_users(self) -> list[User]:
        query = select(User).order_by("id")
        async with self.db.session() as session:
            users = await session.execute(query)
            return users.scalars().all()

    async def get_user_by_id(self, user_id: UUID) -> User | None:
        query = select(User).filter_by(id=user_id)
        async with self.db.session() as session:
            user = await session.execute(query)
            return user.scalar()

    async def get_user_by_username(self, username: str) -> User | None:
        query = select(User).filter_by(username=username)
        async with self.db.session() as session:
            user = await session.execute(query)
            return user.scalar()

    async def create_new_user(self, user_to_create: UserWrite) -> User:
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

    async def deactivate(self, user_id: UUID) -> None:
        query = update(User).where(id=user_id).values(is_active=False)
        async with self.db.session() as session:
            await session.execute(query)

    async def update_role(self, user_id: UUID, new_role: Role) -> None:
        query = update(User).where(id=user_id).values(role=new_role)
        async with self.db.session() as session:
            await session.execute(query)
