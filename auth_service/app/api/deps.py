from typing import Annotated
from uuid import UUID
from fastapi import Depends, Form, HTTPException, Request, status
from fastapi.security import (
    HTTPBearer,
    OAuth2PasswordBearer,
)
import grpc
from jwt import InvalidTokenError

from app.db.session import session_DB
from app.utils.jwt import decode_jwt
from app.schemas.auth import AuthSchema, UserAccessSchema
from app.core.security import verify_secret

from app.crud.auth import get_credential_password_by_user_id
from app.services.auth import AuthService
from gRPC.src.users_service_pb2 import GetUserByEmailResponse
from gRPC.src.users_service_client import UsersServiceClient

http_bearer = HTTPBearer(auto_error=False)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")


# Возвращает обьект с клиентом для общения с сервисом users
def get_user_client(request: Request) -> UsersServiceClient:
    return request.app.state.users_client


def invalid_token_exc(e=None):
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail=f"Invalid token error - {e}",
    )


def get_current_access_token_payload(
    token: Annotated[str, Depends(oauth2_scheme)],
):
    try:
        payload = decode_jwt(token)
        return payload
    except InvalidTokenError as e:
        raise invalid_token_exc(e)


def get_current_refresh_token_payload(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> str:
    return token


def get_auth_service(
    users_client: Annotated[UsersServiceClient, Depends(get_user_client)],
):
    auth_service = AuthService(users_client)
    return auth_service
