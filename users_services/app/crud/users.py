from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.db.models import User
from app.schemas.user import SortBy, SortOrder, UserCreateSchema, UserUpdateSchema, UsersListQuerySchema

from app.core.exceptions import (
    UserNotFoundByIdError,
    UserNotFoundByEmailError,
    UserAlreadyExistsError,
)


async def create_user(user_data: UserCreateSchema, session: AsyncSession):
    user = User(**user_data.model_dump())
    session.add(user)
    try:
        await session.flush()
        await session.refresh(user)
        return user
    except IntegrityError as e:
        raise UserAlreadyExistsError(user.email)


async def deactivate_user(user_id: UUID, session: AsyncSession):
    user = await session.get(User, user_id)

    if user is None:
        raise UserNotFoundByIdError(user_id)

    if user.is_active is False:
        return user

    user.is_active = False
    await session.flush()
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

    await session.flush()
    await session.refresh(user)
    return user

SORT_MAPPED = {
    SortBy.CREATED_AT: User.created_at,
    SortBy.UPDATED_AT: User.updated_at
}

async def get_users(params: UsersListQuerySchema, session: AsyncSession):
    stmt = select(User)
    
    if params.is_active:
        stmt = stmt.where(User.is_active == params.is_active)

    if params.is_verified:
        stmt = stmt.where(User.is_verified == params.is_verified)
        
    sort_column = SORT_MAPPED[params.sort_by]

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
