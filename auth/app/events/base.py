from typing import Any

from aiokafka import AIOKafkaProducer
from pydantic import BaseModel


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
        await kafka_producer.send(**kwargs)
