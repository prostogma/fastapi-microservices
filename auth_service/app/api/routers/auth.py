from typing import Annotated, Any
from fastapi import APIRouter, Depends, Form

from app.schemas.auth import TokenInfo, AuthSchema, UserAccessSchema
from app.utils.jwt import encode_jwt
from app.api.deps import (
    get_auth_service,
    validate_active_auth_user,
    get_current_token_payload,
    get_user_client,
)
from app.db.session import session_DB
from app.services.auth import AuthService
from gRPC.src.users_service_client import UsersServiceClient

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=TokenInfo)
async def auth_user(
    auth_data: Annotated[AuthSchema, Form()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    session: session_DB,
) -> TokenInfo:
    user_access_data: UserAccessSchema = await auth_service.validate_active_auth_user(
        session, auth_data
    )
    jwt_payload = user_access_data.model_dump()

    token = encode_jwt(payload=jwt_payload)
    return TokenInfo(access_token=token)


@router.post("/register", response_model=TokenInfo)
async def register_user(
    register_data: Annotated[AuthSchema, Form()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    session: session_DB,
) -> TokenInfo:
    jwt_payload: UserAccessSchema = await auth_service.register_user(
        session, register_data.username, register_data.password
    )

    token = encode_jwt(payload=jwt_payload.model_dump())
    return TokenInfo(access_token=token)


@router.get("/self")
async def auth_user_check_self_info(
    payload: Annotated[dict, Depends(get_current_token_payload)],
) -> dict[str, Any | None]:
    return {
        "id": payload.get("sub"),
        "email": payload.get("email"),
        "logged_in_at": payload.get("iat"),
    }
