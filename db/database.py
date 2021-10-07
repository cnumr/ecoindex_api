from fastapi.param_functions import Depends
from settings import DATABASE_URL
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import SQLModel, create_engine

connect_args = {"check_same_thread": False}
engine = create_async_engine(DATABASE_URL, future=True, connect_args=connect_args)


async def get_session() -> AsyncSession:
    async with AsyncSession(engine) as session:
        yield session


def is_database_online(session: bool = Depends(get_session)):
    return {"database": bool(session)}


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
