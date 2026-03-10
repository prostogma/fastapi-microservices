import json

from aiokafka import AIOKafkaProducer


class KafkaProducer:
    def __init__(self):
        self._producer = None

    async def start(self):
        self._producer = AIOKafkaProducer(
            bootstrap_servers="localhost:9092",
            value_serializer=lambda v: json.dumps(v).encode("UTF-8"),
        )
        await self._producer.start()

    async def stop(self):
        if self._producer:
            await self._producer.stop()

    async def send_one(self, topic: str, message: dict):
        if self._producer:
            await self._producer.send_and_wait(topic=topic, value=message)


producer = KafkaProducer()
