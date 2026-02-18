from datetime import datetime, timezone
from typing import Any
from uuid import UUID
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Credential, RefreshToken
from app.core.security import verify_secret
from app.core.exceptions import UserNotFoundError


async def get_credential_password_by_user_id(session: AsyncSession, user_id: UUID):
    stmt = select(Credential).where(Credential.user_id == user_id)
    user_in_db = await session.execute(stmt)
    user = user_in_db.scalar_one_or_none()

    if not user:
        return None

    return user.password_hash


async def create_credential(session: AsyncSession, credential_data: dict) -> Credential:
    credential = Credential(**credential_data)
    session.add(credential)
    await session.flush()
    await session.refresh(credential)
    return credential


async def create_refresh_token(session: AsyncSession, auth_data: dict) -> RefreshToken:
    refresh_token = RefreshToken(**auth_data)
    session.add(refresh_token)
    await session.flush()
    await session.refresh(refresh_token)
    return refresh_token


async def enforce_refresh_token_limit(
    session: AsyncSession, user_id: UUID, max_tokens: int = 3
):
    locked_result = await session.execute(
        select(RefreshToken)
        .where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > func.now(),
        )
        .order_by(RefreshToken.created_at.desc())
        .with_for_update()
    )

    tokens = locked_result.scalars().all()

    if len(tokens) < max_tokens:
        return

    tokens_to_revoke = tokens[max_tokens - 1 :]

    tokens_ids = [t.id for t in tokens_to_revoke]

    await session.execute(
        update(RefreshToken)
        .where(RefreshToken.id.in_(tokens_ids))
        .values(revoked_at=func.now())
    )


async def revoke_all_user_tokens(session: AsyncSession, user_id: UUID) -> None:
    stmt = (
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=func.now())
    )
    await session.execute(stmt)


async def revoke_token(session: AsyncSession, hashed_refresh_token: str) -> tuple[UUID | None, bool]:
    stmt = select(RefreshToken).where(RefreshToken.token_hash == hashed_refresh_token)
    result = await session.execute(stmt)
    token_record = result.scalar_one_or_none()
    
    if not token_record:
        return None, False

    if token_record.revoked_at is not None:
        # Токен используется повторно после revoke!
        return token_record.user_id, True
    
    if token_record.expires_at < datetime.now(timezone.utc):
        return None, False
    
    token_record.revoked_at = func.now()
    await session.flush()
    return token_record.user_id, False
    

async def change_user_password(session: AsyncSession, user_id: UUID, new_password: str) -> UUID:
    stmt = (
        update(Credential)
        .where(Credential.user_id == user_id)
        .values(password_hash=new_password, password_updated_at=func.now())
        .returning(Credential.user_id)
    )
    result = await session.execute(stmt)
    updated_credential_user_id = result.scalar_one_or_none()

    if not updated_credential_user_id:
        raise UserNotFoundError("Update failed: user not found")

    return updated_credential_user_id
