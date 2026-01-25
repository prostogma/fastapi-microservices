from typing import Annotated, Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError

from app.db.models import User
from app.core.exceptions import UserNotFoundByEmailError, UserNotFoundByIdError
from app.crud.users import (
    get_user_by_email,
    get_user_by_id,
    get_users,
)
from app.services.users import (
    create_user_service,
    deactivate_user_service,
    update_user_service,
)

from app.db.session import session_DB
from app.schemas.user import (
    UserCreateSchema,
    UserOutSchema,
    UserUpdateSchema,
    UsersListQuerySchema,
)

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserOutSchema, status_code=status.HTTP_201_CREATED)
async def create_user_handler(user_data: UserCreateSchema, session: session_DB) -> User:
    try:
        user = await create_user_service(user_data, session)
        return user
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists",
        )


@router.get("/", response_model=list[UserOutSchema])
async def get_users_handler(
    params: Annotated[UsersListQuerySchema, Depends()], session: session_DB
) -> list[UserOutSchema]:
    users = await get_users(params=params, session=session)
    return users


@router.get("/by-email", response_model=UserOutSchema)
async def get_user_by_email_handler(
    user_email: EmailStr, session: session_DB
) -> UserOutSchema:
    try:
        user = await get_user_by_email(user_email=user_email, session=session)
        return user
    except UserNotFoundByEmailError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{e}")


@router.get("/{user_id}", response_model=UserOutSchema)
async def get_user_by_id_handler(user_id: UUID, session: session_DB) -> UserOutSchema:
    try:
        user = await get_user_by_id(user_id=user_id, session=session)
        return user
    except UserNotFoundByIdError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{e}")


@router.patch("/{user_id}/deactivate", response_model=UserOutSchema)
async def deactivate_user_handler(user_id: UUID, session: session_DB) -> UserOutSchema:
    try:
        user = await deactivate_user_service(user_id=user_id, session=session)
        return user
    except UserNotFoundByIdError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{e}")


@router.patch("/{user_id}", response_model=UserOutSchema)
async def update_user_handler(
    user_id: UUID, user_data: UserUpdateSchema, session: session_DB
) -> UserOutSchema:
    try:
        user = await update_user_service(
            user_id=user_id, user_data=user_data, session=session
        )
        return user
    except UserNotFoundByIdError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{e}")
