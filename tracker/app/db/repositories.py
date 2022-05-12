from dataclasses import dataclass

from sqlalchemy import select

from app.db.models import Task, User
from app.db.session import Database
from app.schemas import TaskWrite


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


@dataclass
class TaskRepository:
    db: Database

    async def get_task_by_id(self, task_id: int) -> Task | None:
        query = select(Task).filter_by(id=task_id)
        async with self.db.session() as session:
            task = await session.execute(query)
            return task.scalar()

    async def create_new_task(self, task_to_create: TaskWrite) -> Task:
        task = Task(**task_to_create.dict())
        async with self.db.session() as session:
            session.add(task)
            await session.commit()
            await session.refresh(task)
        return task
