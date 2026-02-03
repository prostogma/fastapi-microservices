from contextlib import asynccontextmanager
from fastapi import FastAPI

from app.api.routers.auth import router as auth_router
from gRPC.src.users_service_client import create_grpc_channel, UsersServiceClient


@asynccontextmanager
async def lifespan(app: FastAPI):
    channel = create_grpc_channel("localhost:50052")
    app.state.users_client = UsersServiceClient(channel)
    yield
    await app.state.users_client._stub._channel.close()


app = FastAPI(title="Auth service", lifespan=lifespan)

app.include_router(auth_router)
