from fastapi import FastAPI
from contextlib import asynccontextmanager

from consumer import consumer


@asynccontextmanager
async def lifespan(app: FastAPI):
    await consumer.start()
    yield
    await consumer.stop()


app = FastAPI(title="Notification service", lifespan=lifespan)