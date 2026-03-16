from contextlib import asynccontextmanager

import redis.asyncio as redis
from fastapi import FastAPI

from app.api.routers.auth import router as auth_router
from app.schemas.auth import KafkaMessage
from gRPC.src.users_service_client import create_grpc_channel, UsersServiceClient

from kafka_producer import KafkaProducer


@asynccontextmanager
async def lifespan(app: FastAPI):
    # redis
    pool = redis.ConnectionPool.from_url(
        "redis://localhost:6379", decode_responses=True
    )
    app.state.redis = redis.Redis(connection_pool=pool)
    try:
        await app.state.redis.ping()
        print("Succesfully connected to Redis")
    except Exception as e:
        print(f"Redis connection failed: {e}")
    # kafka
    producer = KafkaProducer()
    app.state.producer = producer
    await app.state.producer.start()
    # gRPC
    channel = create_grpc_channel("localhost:50052")
    app.state.users_client = UsersServiceClient(channel)
    
    yield
    
    #redis
    await app.state.redis.close()
    await pool.disconnect()
    # kafka
    await app.state.producer.stop()
    # gRPC
    await app.state.users_client.close()


app = FastAPI(title="Auth service", lifespan=lifespan)


@app.post("/publish")
async def public_kafka_message(data: KafkaMessage):
    message = data.value.model_dump()
    await app.state.producer.send_one("auth.events", message)
    return {"sent": True, "payload": message}


app.include_router(auth_router)
