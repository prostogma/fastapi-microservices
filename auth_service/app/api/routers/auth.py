from typing import Annotated
from fastapi import APIRouter, Depends, Form

from app.schemas.auth import TokenInfo, AuthSchema, UserAccessSchema
from app.utils.jwt import encode_jwt
from app.api.deps import (
    validate_active_auth_user,
    get_current_token_payload,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/token", response_model=TokenInfo)
async def auth_user(
    auth_data: Annotated[UserAccessSchema, Depends(validate_active_auth_user)],
) -> TokenInfo:
    jwt_payload = auth_data.model_dump()

    token = encode_jwt(payload=jwt_payload)
    return TokenInfo(access_token=token)

# @router.post("/register", response_model=TokenInfo)
# async def register_user()


@router.get("/self")
async def auth_user_check_self_info(
    payload: Annotated[dict, Depends(get_current_token_payload)],
): 
    return {
        "email": payload.get("sub"),
        "logged_in_at": payload.get("iat")
    }
