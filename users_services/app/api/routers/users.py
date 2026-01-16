from typing import Annotated, Sequence
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import EmailStr
from sqlalchemy.exc import IntegrityError

from app.db.models import User
from app.core.exceptions import UserNotFoundByEmailError, UserNotFoundByIdError
from app.crud.users import (
    create_user,
    deactivate_user,
    get_user_by_email,
    get_user_by_id,
    get_users,
    update_user,
)
from app.db.session import session_DB
from app.schemas.user import UserCreateSchema, UserOutSchema, UserUpdateSchema, UsersListQuerySchema

router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserOutSchema, status_code=status.HTTP_201_CREATED)
async def create_user_handler(user_data: UserCreateSchema, session: session_DB) -> User:
    """
    Создает нового пользователя в базе.

    Args:
        user_data (UserCreateSchema): Схема для создания пользователя.
        session (session_DB): Сессия для взаимодействия с БД.

    Raises:
        HTTPException: Ошибка, указывающая на то что email занят.

    Returns:
        UserOutSchema: Экземпляр схемы для возврата данных о пользователе.
    """
    try:
        user = await create_user(user_data=user_data.model_dump(), session=session)
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
    """
    Вытаскивает пользователя из базы по email.

    Args:
        user_email (EmailStr): Email по которому будет вытаскиваться пользователь.
        session (session_DB): Сессия для работы с базой.

    Raises:
        HTTPException: Ошибка указывающая на то, что пользователь с таким email не найден.

    Returns:
        UserOutSchema: Экземпляр схемы для возврата данных о пользователе.
    """
    try:
        user = await get_user_by_email(user_email=user_email, session=session)
        return user
    except UserNotFoundByEmailError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{e}")


@router.get("/{user_id}", response_model=UserOutSchema)
async def get_user_by_id_handler(user_id: UUID, session: session_DB) -> UserOutSchema:
    """
    Получает пользователя по id (user_id).

    Args:
        user_id (UUID): Id, по которому мы будем доставать пользователя из базы.
        session (session_DB): Сессия для работы с базой.

    Raises:
        HTTPException: Ошибка указывающая на то, что пользователь с таким email не найден.

    Returns:
        UserOutSchema: Экземпляр схемы для возврата данных о пользователе.
    """
    try:
        user = await get_user_by_id(user_id=user_id, session=session)
        return user
    except UserNotFoundByIdError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{e}")


@router.patch("/{user_id}/deactivate", response_model=UserOutSchema)
async def deactivate_user_handler(user_id: UUID, session: session_DB) -> UserOutSchema:
    """
    Вводит пользователя в инактивное состояние.

    Args:
        user_id (UUID): Идентификатор, по которому пользователь достается из базы.
        session (session_DB): Сессия для работы с базой.

    Raises:
        HTTPException: Ошибка указывающая на то, что пользователь с таким email не найден.

    Returns:
        UserOutSchema: Экземпляр схемы для возврата данных о пользователе.
    """
    try:
        user = await deactivate_user(user_id=user_id, session=session)
        return user
    except UserNotFoundByIdError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{e}")


@router.patch("/{user_id}", response_model=UserOutSchema)
async def update_user_handler(
    user_id: UUID, user_data: UserUpdateSchema, session: session_DB
) -> UserOutSchema:
    """
    Обновляет данные пользователя.

    Args:
        user_id (UUID): Идентификатор, по которому пользователь достается из базы.
        user_data (UserUpdateSchema): Данные для обновления пользователя.
        session (session_DB): Сессия для работы с базой.

    Raises:
        HTTPException: Ошибка указывающая на то, что пользователь с таким email не найден.

    Returns:
        UserOutSchema: Экземпляр схемы для возврата данных о пользователе.
    """
    try:
        user = await update_user(user_id=user_id, user_data=user_data, session=session)
        return user
    except UserNotFoundByIdError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{e}")
