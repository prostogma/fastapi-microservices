from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.routers.auth import router as auth_router
from app.schemas.auth import KafkaMessage
from gRPC.src.users_service_client import create_grpc_channel, UsersServiceClient

from kafka_producer import producer


@asynccontextmanager
async def lifespan(app: FastAPI):
    #kafka
    await producer.start()
    #gRPC
    channel = create_grpc_channel("localhost:50052")
    app.state.users_client = UsersServiceClient(channel)
    yield
    #kafka
    await producer.stop()
    #gRPC
    await app.state.users_client.close()


app = FastAPI(title="Auth service", lifespan=lifespan)

@app.post("/publish")
async def public_kafka_message(data: KafkaMessage):
    message = {"key": data.key, "value": data.value}
    await producer.send_one("my-topic", message)
    return {"sent": True, "payload": message}
    
    
app.include_router(auth_router)
