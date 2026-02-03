import gRPC.src.users_service_pb2 as pb
import gRPC.src.users_service_pb2_grpc as grpc_pb
import grpc
from grpc.aio import Channel


def create_grpc_channel(target: str) -> Channel:
    return grpc.aio.insecure_channel(target)


class UsersServiceClient:
    def __init__(self, channel: Channel):
        self._channel = channel
        self._stub = grpc_pb.UserServiceStub(channel)

    async def get_user_by_email(self, email: str) -> pb.GetUserByEmailResponse | None:
        try:
            response = await self._stub.GetUserByEmail(pb.GetUserByEmailRequest(email=email))
            return response
        except grpc.aio.AioRpcError as e:
            if e.code() == grpc.StatusCode.NOT_FOUND:
                return None
            else:
                raise RuntimeError(f"Ошибка gRPC: {e.code()} - {e.details()}")
    
    async def create_user_by_email(self, email: str) -> pb.GetUserByEmailResponse | None:
        try:
            response = await self._stub.CreateUserByEmail(pb.GetUserByEmailRequest(email=email))
            return response
        except grpc.aio.AioRpcError as e:
            if e.code() == grpc.StatusCode.ALREADY_EXISTS:
                return None
            elif e.code() == grpc.StatusCode.INVALID_ARGUMENT:
                raise ValueError(f"Некоректный email: {email}")
            else:
                raise RuntimeError(f"Ошибка gRPC: {e.code()} - {e.details()}")
    
    async def close(self):
        await self._channel.close()