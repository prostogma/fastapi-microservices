from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User
from app.schemas.user import SortBy, SortOrder, UserUpdateSchema, UsersListQuerySchema

from app.core.exceptions import UserNotFoundByIdError, UserNotFoundByEmailError


async def create_user(user_data: dict, session: AsyncSession):
    user = User(**user_data)
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


async def deactivate_user(user_id: UUID, session: AsyncSession):
    user = await session.get(User, user_id)

    if user is None:
        raise UserNotFoundByIdError(user_id)

    if user.is_active is False:
        return user

    user.is_active = False
    await session.commit()
    await session.refresh(user)
    return user


async def update_user(
    user_id: UUID, user_data: UserUpdateSchema, session: AsyncSession
):
    user = await session.get(User, user_id)

    if user is None:
        raise UserNotFoundByIdError(user_id)

    update_data = user_data.model_dump(exclude_unset=True)

    if not update_data:
        return user

    has_changes = False

    for field, value in update_data.items():
        if getattr(user, field) != value:
            setattr(user, field, value)
            has_changes = True

    if not has_changes:
        return user

    await session.commit()
    await session.refresh(user)
    return user

SORT_MAPPED = {
    SortBy.CREATED_AT: User.created_at,
    SortBy.UPDATED_AT: User.updated_at
}

async def get_users(params: UsersListQuerySchema, session: AsyncSession):
    stmt = select(User)
    
    if params.is_active is not None:
        stmt = stmt.where(User.is_active == params.is_active)

    if params.is_verified is not None:
        stmt = stmt.where(User.is_verified == params.is_verified)
        
    sort_column = SORT_MAPPED.get(params.sort_by)

    if params.sort_order == SortOrder.DESC:
        stmt = stmt.order_by(sort_column.desc(), User.id.asc())
    else:
        stmt = stmt.order_by(sort_column.asc(), User.id.asc())

    stmt = stmt.limit(params.limit).offset(params.offset)

    result = await session.execute(stmt)
    users = result.scalars().all()
    return users

async def get_user_by_id(user_id: UUID, session: AsyncSession):
    user = await session.get(User, user_id)

    if not user:
        raise UserNotFoundByIdError(user_id)

    return user

async def get_user_by_email(user_email: str, session: AsyncSession):
    stmt = select(User).where(User.email == user_email)
    result = await session.execute(stmt)
    user = result.scalar_one_or_none()
    
    if not user:
        raise UserNotFoundByEmailError(user_email)

    return user
