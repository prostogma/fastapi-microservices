from typing import Annotated
from uuid import UUID
from fastapi import Depends, Form, HTTPException, Request, status
from fastapi.security import (
    HTTPBearer,
    HTTPAuthorizationCredentials,
    OAuth2PasswordBearer,
)
import grpc
from jwt import InvalidTokenError

from app.db.session import session_DB
from app.utils.jwt import decode_jwt
from app.schemas.auth import AuthSchema, UserAccessSchema
from app.core.security import hash_secret, verify_secret

from app.crud.auth import get_credential_password_by_user_id
from app.services.auth import AuthService
from gRPC.src.users_service_pb2 import GetUserByEmailResponse
from gRPC.src.users_service_client import UsersServiceClient

# http_bearer = HTTPBearer()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


# Возвращает обьект с клиентом для общения с сервисом users
def get_user_client(request: Request) -> UsersServiceClient:
    return request.app.state.users_client


def invalid_token_exc(e=None):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Invalid token error - {e}",
    )


async def validate_active_auth_user(
    auth_data: Annotated[AuthSchema, Form()],
    users_client: Annotated[UsersServiceClient, Depends(get_user_client)],
    session: session_DB,
) -> GetUserByEmailResponse:
    unauthed_exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password!"
    )

    try:
        user_data = await users_client.get_user_by_email(auth_data.username)
    except grpc.aio.AioRpcError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"User service error - {e}",
        )

    if not user_data:
        raise unauthed_exc

    if not user_data.is_active or not user_data.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User inactive or no verified!",
        )

    user_password = await get_credential_password_by_user_id(
        session, UUID(user_data.id)
    )

    if not user_password:
        raise unauthed_exc

    if not verify_secret(auth_data.password, user_password):
        raise unauthed_exc

    user_access_data = UserAccessSchema(
        sub=user_data.id, email=auth_data.username
    )

    return user_access_data


def get_current_token_payload(
    token: Annotated[str, Depends(oauth2_scheme)],
):
    try:
        payload = decode_jwt(token)
        return payload
    except InvalidTokenError as e:
        raise invalid_token_exc(e)

def get_auth_service(users_client: Annotated[UsersServiceClient, Depends(get_user_client)]):
    auth_service = AuthService(users_client)
    return auth_service
