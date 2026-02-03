from typing import Annotated
from fastapi import APIRouter, Depends, Form

from app.schemas.auth import TokenInfo, AuthSchema, UserAccessSchema
from app.utils.jwt import encode_jwt
from app.api.deps import (
    validate_active_auth_user,
    get_current_token_payload,
    get_user_client
)
from app.db.session import session_DB
from app.services.registration import RegistrationService
from gRPC.src.users_service_client import UsersServiceClient

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=TokenInfo)
async def auth_user(
    auth_data: Annotated[UserAccessSchema, Depends(validate_active_auth_user)],
) -> TokenInfo:
    jwt_payload = auth_data.model_dump()

    token = encode_jwt(payload=jwt_payload)
    return TokenInfo(access_token=token)


@router.post("/register", response_model=TokenInfo)
async def register_user(
    register_data: Annotated[AuthSchema, Form()],
    users_client: Annotated[UsersServiceClient, Depends(get_user_client)],
    session: session_DB
) -> TokenInfo:
    service = RegistrationService(users_client)
    jwt_payload: UserAccessSchema = await service.register_user(session, register_data.username, register_data.password)
    
    token = encode_jwt(payload=jwt_payload.model_dump())
    return TokenInfo(access_token=token)


@router.get("/self")
async def auth_user_check_self_info(
    payload: Annotated[dict, Depends(get_current_token_payload)],
): 
    return {
        "email": payload.get("sub"),
        "logged_in_at": payload.get("iat")
    }
