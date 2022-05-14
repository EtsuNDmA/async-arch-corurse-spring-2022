import json
from collections import defaultdict

import aiorun
from aiokafka import AIOKafkaConsumer, ConsumerRecord
from loguru import logger

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
            headers = get_headers(msg)
            if "UserCreated" in headers.get("event_name", []):
                logger.debug("Got message {}", msg)
                await user_repository.create_new_user(UserWrite.parse_obj(get_data(msg)))
    finally:
        await consumer.stop()
        await db.disconnect()


def get_headers(msg: ConsumerRecord) -> dict[str, list[str]]:
    headers = defaultdict(list)
    for key, value in msg.headers:
        headers[key].append(value.decode())
    return headers


def get_data(msg: ConsumerRecord):
    obj = json.loads(msg.value.decode())
    return obj.get("data")


if __name__ == "__main__":
    configure_logger(settings)
    aiorun.run(main(), use_uvloop=True)
