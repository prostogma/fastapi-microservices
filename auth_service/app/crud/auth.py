from typing import Any
from uuid import UUID
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Credential, RefreshToken


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


async def revoke_all_user_tokens(session: AsyncSession, user_id: UUID):
    stmt = (
        update(RefreshToken)
        .where(RefreshToken.user_id == user_id, RefreshToken.revoked_at.is_(None))
        .values(revoked_at=func.now())
    )
    await session.execute(stmt)


async def revoke_token(session: AsyncSession, hashed_refresh_token: str) -> UUID | None:
    stmt = (
        update(RefreshToken)
        .where(
            RefreshToken.token_hash == hashed_refresh_token,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > func.now(),
        )
        .values(revoked_at=func.now())
        .returning(RefreshToken.user_id)
    )
    result = await session.execute(stmt)
    row = result.first()
    if row:
        return row[0]  # user_id

    return None
