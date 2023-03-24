from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)

from app.config import Config


async def get_database_session(config: Config) -> async_sessionmaker[AsyncSession]:
    engine = create_async_engine(config.DATABASE_URI)
    session = async_sessionmaker(engine)
    return session
