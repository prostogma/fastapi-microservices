import grpc
import asyncio
from grpc import aio
from pydantic import ValidationError
from gRPC.src import users_service_pb2_grpc as grpc_pb
from gRPC.src import users_service_pb2 as pb

from app.db.session import async_session_maker
from app.crud.users import create_user, get_user_by_email
from app.core.exceptions import UserAlreadyExistsError, UserNotFoundByEmailError
from app.schemas.user import UserCreateSchema


class UserServiceServicer(grpc_pb.UserServiceServicer):
    async def GetUserByEmail(
        self, request, context
    ) -> pb.GetUserByEmailResponse | None:
        async with async_session_maker() as session:
            try:
                user = await get_user_by_email(request.email, session)
                response = pb.GetUserByEmailResponse(
                    id=str(user.id),
                    is_active=user.is_active,
                    is_verified=user.is_verified,
                )
                return response
            except UserNotFoundByEmailError:
                await context.abort(
                    grpc.StatusCode.NOT_FOUND,
                    f"User with email {request.email} not found",
                )

    async def CreateUserByEmail(
        self, request, context
    ) -> pb.GetUserByEmailResponse | None:
        async with async_session_maker() as session:
            try:
                user_data = UserCreateSchema(
                    email=request.email, is_active=True, is_verified=True
                )  # is_verified: True - заглушка до момента создания notification service
                user = await create_user(user_data.model_dump(), session)
                await session.commit()
                response = pb.GetUserByEmailResponse(
                    id=str(user.id), is_active=user.is_active, is_verified=user.is_verified
                )
                return response
            except ValidationError as e:
                session.rollback()
                await context.abort(grpc.StatusCode.INVALID_ARGUMENT, str(e))
            except UserAlreadyExistsError as e:
                session.rollback()
                await context.abort(grpc.StatusCode.ALREADY_EXISTS, str(e))


async def server():
    server = aio.server()
    grpc_pb.add_UserServiceServicer_to_server(UserServiceServicer(), server)
    server.add_insecure_port("0.0.0.0:50051")
    await server.start()
    await server.wait_for_termination()


if __name__ == "__main__":
    asyncio.run(server())
