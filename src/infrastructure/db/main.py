from sqlalchemy.dialects.mysql.aiomysql import AsyncAdapt_aiomysql_connection
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from src.core.config import settings

_orig_ping = AsyncAdapt_aiomysql_connection.ping

def _patched_ping(self, reconnect=False):
    return _orig_ping(self, reconnect)

AsyncAdapt_aiomysql_connection.ping = _patched_ping


class Base(DeclarativeBase):
    pass


async_engine = create_async_engine(
    settings.database_url,
    pool_size=settings.POOL_SIZE,
    max_overflow=settings.MAX_OVERFLOW,
    pool_pre_ping=True,
)

session_maker = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_session() -> AsyncSession:
    async with session_maker() as session:
        yield session
