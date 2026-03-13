import json
import asyncio

from aiokafka import AIOKafkaConsumer

from app.core.mailer import mailer


class KafkaConsumer:
    def __init__(self):
        self._consumer = None
        self._consumer_task = None
        self._is_running = False

    async def start(self):
        self._consumer = AIOKafkaConsumer(
            "auth.events",
            bootstrap_servers="localhost:9092",
            value_deserializer=lambda v: json.loads(v),
            auto_offset_reset="latest",
        )
        await self._consumer.start()
        self._is_running = True
        self._consumer_task = asyncio.create_task(self.consume())

    async def consume(self):
        try:
            async for msg in self._consumer:
                payload = msg.value
                print(f"{payload=}")
                event_type = payload.get("event_type")
                print(f"{event_type=}")
                data = payload.get("data")
                print(f"{data=}")

                if event_type == "user_registered":
                    email = data.get("email")
                    token = data.get("token")

                    if email and token:
                        await mailer.send_registration_email(
                            recipient=email, token=token
                        )
                    else:
                        print("Error: the message is missing data or token")
                else:
                    print(f"Неизвестный тип события: {event_type}")

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
