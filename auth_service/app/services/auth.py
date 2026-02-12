from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import UUID
from fastapi import HTTPException, status
import grpc
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.auth import (
    create_credential,
    create_refresh_token,
    enforce_refresh_token_limit,
    get_credential_password_by_user_id,
    revoke_all_user_tokens,
    revoke_token,
)
from app.schemas.auth import (
    AuthSchema,
    CredentialCreateSchema,
    TokenInfo,
    UserAccessSchema,
)
from app.core.security import hash_refresh_token, hash_secret, verify_secret
from app.utils.refresh_token import generate_refresh_token
from app.utils.jwt import encode_jwt
from gRPC.src import users_service_pb2 as pb
from gRPC.src.users_service_client import UsersServiceClient
from app.core.config import settings


class AuthService:
    def __init__(self, users_client: UsersServiceClient):
        self.users_client = users_client  # gRPC клиент для users

    async def register_user(self, session: AsyncSession, email: str, password: str):
        try:
            user_data: pb.GetUserByEmailResponse = (
                await self.users_client.create_user_by_email(email)
            )

            if user_data is None:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"User with email - {email} already exist",
                )

        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except RuntimeError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
            )

        hashed_password = hash_secret(password)
        credential_data = CredentialCreateSchema(
            user_id=user_data.id, password_hash=hashed_password
        )

        await create_credential(session, credential_data.model_dump())

        return UserAccessSchema(sub=user_data.id)

    async def validate_active_auth_user(
        self, session: AsyncSession, auth_data: AuthSchema
    ) -> UserAccessSchema:

        unauthed_exc = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password!",
        )

        try:
            user_data = await self.users_client.get_user_by_email(auth_data.username)
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

        user_access_data = UserAccessSchema(sub=user_data.id)

        return user_access_data

    async def generate_refresh_token(self, session: AsyncSession, user_id: UUID) -> str:
        await enforce_refresh_token_limit(session, user_id)

        token = generate_refresh_token()
        expires_at = datetime.now(timezone.utc) + timedelta(
            days=settings.auth_jwt.refresh_token_expire_days
        )

        auth_data = {
            "user_id": user_id,
            "token_hash": hash_refresh_token(token),
            "expires_at": expires_at,
        }

        await create_refresh_token(session, auth_data)

        return token

    async def refresh_access_token(
        self, session: AsyncSession, refresh_token: str
    ) -> TokenInfo:
        hashed_refresh_token = hash_refresh_token(refresh_token)
        user_id = await revoke_token(session, hashed_refresh_token)

        if not user_id:
            await revoke_all_user_tokens(session, user_id)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token"
            )

        access_token_data = UserAccessSchema(sub=str(user_id))
        access_token = encode_jwt(payload=access_token_data.model_dump())

        new_refresh_token = await self.generate_refresh_token(session, user_id)

        return TokenInfo(access_token=access_token, refresh_token=new_refresh_token)
