from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import func, select, update
from sqlalchemy.orm import joinedload

from app.api.schemas import TaskWrite, UserWrite
from app.db.models import Role, Task, User
from app.db.session import Database

CAN_BE_TASK_ASSIGNEE = (Role.DEVELOPER, Role.ACCOUNTANT)


@dataclass
class UserRepository:
    db: Database

    async def create_new_user(self, user_to_create: UserWrite) -> User:
        user = User(**user_to_create.dict())
        async with self.db.session() as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)
        return user


@dataclass
class TaskRepository:
    db: Database

    async def get_all_tasks(self) -> list[Task]:
        query = select(Task).join(Task.assignee).options(joinedload(Task.assignee)).order_by("id")
        async with self.db.session() as session:
            tasks = await session.execute(query)
            return tasks.scalars().all()

    async def get_task_by_id(self, task_id: int) -> Task | None:
        query = select(Task).filter_by(id=task_id).join(Task.assignee).options(joinedload(Task.assignee))
        async with self.db.session() as session:
            task = await session.execute(query)
            return task.scalar()

    async def create_task(self, task_to_create: TaskWrite) -> Task:
        async with self.db.session() as session:
            random_assignee_id = (
                select(User.id).where(User.role.in_(CAN_BE_TASK_ASSIGNEE)).order_by(func.random()).limit(1)
            )
            task = Task(assignee_id=random_assignee_id, **task_to_create.dict())
            session.add(task)
            await session.commit()
        return await self.get_task_by_id(task.id)

    async def shuffle_tasks(self) -> None:
        random_assignee_id = (
            select(User.id)
            .where(
                Task.id > 0,  # we need correlation to create random assignee_id for each row
                User.role.in_(CAN_BE_TASK_ASSIGNEE),
            )
            .order_by(func.random())
            .limit(1)
            .scalar_subquery()
        )
        async with self.db.session() as session:
            query = update(Task).values(assignee_id=random_assignee_id)
            await session.execute(query)
            await session.commit()
        return None
