from typing import Annotated
from fastapi import Depends
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.core.config import settings


engine = create_async_engine(url=settings.DATABASE_URL)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


async def create_async_session():
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception as e:
            await session.rollback()
            print(f"Ошибка при работе с сессией - {e}")
            raise

session_DB = Annotated[AsyncSession, Depends(create_async_session)]