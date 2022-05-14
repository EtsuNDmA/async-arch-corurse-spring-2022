import aiorun
from aiokafka import AIOKafkaConsumer
from app.api.schemas import UserWrite
from app.db.repositories import UserRepository
from app.db.session import Database
from app.settings.config import settings
from app.settings.logger import configure_logger


async def main():
    db = Database(
        db_connect_url=settings.database_connection_url,
        echo=settings.DEBUG,
    )
    user_repository = UserRepository(db)
    consumer = AIOKafkaConsumer(
        settings.KAFKA_USER_STREAMING_TOPIC,
        bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
        group_id=settings.KAFKA_GROUP_ID,
    )
    await consumer.start()
    try:
        async for msg in consumer:
            await user_repository.create_new_user(UserWrite.parse_raw(msg.value))
    finally:
        await consumer.stop()
        await db.disconnect()


if __name__ == "__main__":
    configure_logger(settings)
    aiorun.run(main(), use_uvloop=True)
