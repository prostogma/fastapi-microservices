from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.crud.auth import create_credential
from app.schemas.auth import CredentialCreateSchema, UserAccessSchema
from app.core.security import hash_secret
from gRPC.src import users_service_pb2 as pb
from gRPC.src.users_service_client import UsersServiceClient


class RegistrationService:
    def __init__(self, users_client: UsersServiceClient):
        self.users_client = users_client    # gRPC клиент для users

    async def register_user(self, session: AsyncSession, email: str, password: str):
        try:
            user_data: pb.GetUserByEmailResponse = (
                await self.users_client.create_user_by_email(email)
            )
            if user_data is None:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"User with email - {email} already exist")

        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except RuntimeError as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))

        hashed_password = hash_secret(password)
        credential_data = CredentialCreateSchema(user_id=user_data.id, password_hash=hashed_password)
        
        await create_credential(session, credential_data.model_dump())

        return UserAccessSchema(sub=user_data.id, email=email)
