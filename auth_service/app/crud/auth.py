from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Credential


async def get_credential_password_by_user_id(session: AsyncSession, user_id: UUID):
    stmt = select(Credential).where(Credential.user_id == user_id)
    user_in_db = await session.execute(stmt)
    user = user_in_db.scalar_one_or_none()

    if not user:
        return None
    
    return user.password_hash
    
    
