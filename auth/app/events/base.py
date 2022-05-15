import json
from typing import Any

from aiokafka import AIOKafkaProducer
from app.settings.config import settings
from jsonschema.exceptions import ValidationError
from loguru import logger
from pydantic import BaseModel

from schema_registry.validator import Validator

validator = Validator(settings.SCHEMAS_ROOT_PATH)


class EventMeta(BaseModel):
    version: int = 1
    name: str


class Event(BaseModel):
    meta: EventMeta
    data: Any

    @property
    def key(self) -> None:
        return None

    async def send(self, kafka_producer: AIOKafkaProducer, topic: str) -> None:
        value_json = self.json()
        kwargs = dict(
            topic=topic,
            value=value_json.encode(),
            key=str(self.key).encode(),
            headers=[
                ("event_version", str(self.meta.version).encode()),
                ("event_name", self.meta.name.encode()),
            ],
        )
        try:
            # TODO fix double serialization/deserialization
            await validator.validate(
                json.loads(value_json),
                self.meta.name,
                self.meta.version,
            )
            logger.debug("Send event {}", kwargs)
            await kafka_producer.send(**kwargs)
        except ValidationError:
            logger.exception("Failed to send message due to schema validation error")
