from asyncio import current_task
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from loguru import logger
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    create_async_engine,
)
from sqlalchemy.orm import as_declarative, declared_attr, sessionmaker


@as_declarative()
class Base:
    id: Any
    __name__: str

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()


class Database:
    def __init__(self, db_connect_url: str, **connection_kwargs: Any) -> None:
        self._engine = create_async_engine(url=db_connect_url, **connection_kwargs)
        self._async_session_factory = async_scoped_session(
            sessionmaker(
                autocommit=False,
                autoflush=False,
                class_=AsyncSession,
                expire_on_commit=False,
                bind=self._engine,
            ),
            scopefunc=current_task,
        )

    async def create_tables(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    @asynccontextmanager
    async def session(self) -> AsyncGenerator[AsyncSession, None]:
        session: AsyncSession = self._async_session_factory()
        try:
            yield session
        except Exception:
            logger.warning("Session rollback because of exception")
            await session.rollback()
            raise
        finally:
            await session.close()
            await self._async_session_factory.remove()

    async def disconnect(self) -> None:
        await self._engine.dispose()
