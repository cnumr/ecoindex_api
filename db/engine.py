from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool
from sqlmodel import SQLModel
from sqlmodel.ext.asyncio.session import AsyncSession

from settings import Settings

engine = create_async_engine(
    Settings().DATABASE_URL, future=True, pool_pre_ping=True, poolclass=NullPool
)


async def get_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
