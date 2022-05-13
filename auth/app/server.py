import asyncio

import uvloop
from aiokafka import AIOKafkaConsumer, AIOKafkaProducer
from app.api.routers import router
from app.db.session import Database
from app.settings.config import AppSettings, settings
from app.settings.logger import configure_logger
from fastapi import FastAPI
from loguru import logger

asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())


class Application:
    def __init__(self, settings: AppSettings):
        configure_logger(settings)

        self.app = FastAPI(
            title="Auth API",
            description="Auth service for Popug Inc.",
            debug=settings.DEBUG,
        )
        self.app.state.config = settings
        self.add_middlewares(settings)
        self.configure_hooks()
        self.register_urls()

    @property
    def fastapi_app(self) -> FastAPI:
        return self.app

    def configure_hooks(self) -> None:
        self.setup_exception_handlers()
        self.app.add_event_handler("startup", self.create_databases_and_tables)
        self.app.add_event_handler("startup", self.create_kafka_producer)
        self.app.add_event_handler("startup", self.create_kafka_consumer)

        self.app.add_event_handler("shutdown", self.close_database_pool)
        self.app.add_event_handler("shutdown", self.close_kafka_producer)
        self.app.add_event_handler("shutdown", self.close_kafka_consumer)

    def register_urls(self) -> None:
        self.app.include_router(router)

    def setup_exception_handlers(self) -> None:
        pass

    def add_middlewares(self, settings: AppSettings) -> None:
        pass

    async def create_database_pool(self) -> None:
        db = Database(
            db_connect_url=settings.database_connection_url,
            echo=settings.DEBUG,
        )
        logger.info("Creating database connection")
        self.app.state.db = db

    async def create_kafka_producer(self) -> None:
        producer = AIOKafkaProducer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
        await producer.start()
        self.app.state.producer = producer

    async def close_kafka_producer(self) -> None:
        producer = self.app.state.producer
        await producer.stop()

    async def create_kafka_consumer(self) -> None:
        consumer = AIOKafkaConsumer(bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS)
        await consumer.start()
        self.app.state.consumer = consumer

    async def close_kafka_consumer(self) -> None:
        consumer = self.app.state.consumer
        await consumer.stop()

    async def close_database_pool(self) -> None:
        logger.info("Closing database pool")
        try:
            await self.app.state.db.disconnect()
        except Exception as exc:
            logger.warning("failed to close database pool due to {}", exc)

    async def create_databases_and_tables(self) -> None:
        await self.create_database_pool()
        await self.app.state.db.create_tables()


app = Application(settings=settings).fastapi_app
