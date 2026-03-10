import json

from aiokafka import AIOKafkaConsumer
import asyncio


class KafkaConsumer:
    def __init__(self):
        self._consumer = None
        self._consumer_task = None
        self._is_running = False
    
    async def start(self):
        self._consumer = AIOKafkaConsumer(
            "my-topic",
            bootstrap_servers="localhost:9092",
            value_deserializer=lambda v: json.loads(v),
            auto_offset_reset="latest"
        )
        await self._consumer.start()
        self._is_running = True
        self._consumer_task = asyncio.create_task(self.consume())
    
    async def consume(self):
        try:
            async for msg in self._consumer:
                print(f"[->]{msg.topic}[->]{msg.offset}[->]{msg.value}")
                if not self._is_running:
                    break
        except Exception as e:
            print(f"Kafka consumpting error: {e}")
    
    async def stop(self):
        self._is_running = False
        if self._consumer:
            await self._consumer.stop()
        if self._consumer_task:
            self._consumer_task.cancel()


consumer = KafkaConsumer()