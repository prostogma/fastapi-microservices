from typing import Annotated, Any
from uuid import UUID
from fastapi import APIRouter, Depends, Form, Response, status

from app.schemas.auth import ChangePassword, TokenInfo, AuthSchema, UserAccessSchema
from app.utils.jwt import encode_jwt
from app.api.deps import (
    get_auth_service,
    get_current_access_token_payload,
    get_current_refresh_token_payload,
    http_bearer,
)
from app.db.session import session_DB
from app.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["auth"], dependencies=[Depends(http_bearer)])


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
    refresh_token = await auth_service.generate_refresh_token(
        session, jwt_payload["sub"]
    )

    token = encode_jwt(payload=jwt_payload)
    return TokenInfo(access_token=token, refresh_token=refresh_token)


@router.post("/refresh", response_model=TokenInfo)
async def refresh_access_token(
    session: session_DB,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    refresh_token: Annotated[str, Depends(get_current_refresh_token_payload)],
) -> TokenInfo:
    tokens_info = await auth_service.refresh_access_token(session, refresh_token)
    return tokens_info


@router.post("/register", response_model=TokenInfo)
async def register_user(
    register_data: Annotated[AuthSchema, Form()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    session: session_DB,
) -> TokenInfo:
    jwt_payload: UserAccessSchema = await auth_service.register_user(
        session, register_data.username, register_data.password
    )

    refresh_token = await auth_service.generate_refresh_token(session, jwt_payload.sub)

    token = encode_jwt(payload=jwt_payload.model_dump())
    return TokenInfo(access_token=token, refresh_token=refresh_token)


@router.get("/self")
async def auth_user_check_self_info(
    payload: Annotated[dict, Depends(get_current_access_token_payload)],
) -> dict[str, Any | None]:
    return {
        "id": payload.get("sub"),
        "logged_in_at": payload.get("iat"),
    }


@router.post("/change-password")
async def change_user_password(
    session: session_DB,
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
    data: ChangePassword,
    payload: Annotated[dict, Depends(get_current_access_token_payload)],
):
    user_id = payload.get("sub")

    await auth_service.change_user_password(session, data, UUID(user_id))
    return Response(status_code=status.HTTP_204_NO_CONTENT)
