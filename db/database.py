from fastapi.param_functions import Depends
from settings import DATABASE_URL
from sqlmodel import Session, SQLModel, create_engine

engine = create_engine(DATABASE_URL)


def get_session():
    with Session(engine) as session:
        yield session


def is_database_online(session: bool = Depends(get_session)):
    return {"database": bool(session)}


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
