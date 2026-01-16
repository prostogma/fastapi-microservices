from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

# Создаем асинхронный движок для работы с БД
engine = create_async_engine(url=DATABASE_URL)

# Создаем асинхронную фабрику сессий для взаимодействия с БД
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

async def create_async_session():
    async with async_session_maker() as session:
        try:
            yield session
        except Exception as e:
            await session.rollback()
            print(f"Ошибка при работе с сессией - {e}")
            raise

session_DB = Annotated[AsyncSession, Depends(create_async_session)]

# # Декоратор для выдачи функциям сессий
# def connection(method):
#     async def wrapper(*args, **kwargs):
#         async with async_session_maker() as session:
#             try:
#                 return await method(*args, session=session, **kwargs)
#             except Exception as e:
#                 await session.rollback()
#                 raise e

#     return wrapper
