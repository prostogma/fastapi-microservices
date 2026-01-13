from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from app.core.config import settings

DATABASE_URL = settings.DATABASE_URL

# Создаем асинхронный движок для работы с БД
engine = create_async_engine(url=DATABASE_URL)

# Создаем асинхронную фабрику сессий для взаимодействия с БД
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

# Декоратор для выдачи функциям сессий
def connection(method):
    async def wrapper(*args, **kwargs):
        async with async_session_maker() as session:
            try:
                return await method(*args, session=session, **kwargs)
            except Exception as e:
                await session.rollback()
                raise e

    return wrapper
