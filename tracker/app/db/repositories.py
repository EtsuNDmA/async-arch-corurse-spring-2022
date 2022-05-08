from app.db.models import User

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
