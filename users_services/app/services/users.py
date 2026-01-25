from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.user import UserCreateSchema, UserUpdateSchema
from app.crud.users import create_user, deactivate_user, update_user
from app.db.models import User


async def create_user_service(
    user_data: UserCreateSchema, session: AsyncSession
) -> User:
    async with session.begin():
        return await create_user(user_data, session)


async def deactivate_user_service(user_id: UUID, session: AsyncSession):
    async with session.begin():
        return await deactivate_user(user_id, session)


async def update_user_service(
    user_id: UUID, user_data: UserUpdateSchema, session: AsyncSession
):
    async with session.begin():
        return await update_user(user_id, user_data, session)
