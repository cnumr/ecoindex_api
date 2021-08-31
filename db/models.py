from uuid import uuid4

from sqlalchemy import Column
from sqlalchemy.sql.sqltypes import DateTime, Float, Integer, String

from .database import Base


def generate_uuid():
    return str(uuid4())


class Ecoindex(Base):
    __tablename__ = "ecoindex"

    id = Column(type_=String, primary_key=True, default=generate_uuid)
    url = Column(type_=String)
    host = Column(type_=String)
    date = Column(type_=DateTime)
    width = Column(type_=Integer)
    height = Column(type_=Integer)
    size = Column(type_=Float)
    nodes = Column(type_=Integer)
    requests = Column(type_=Integer)
    grade = Column(type_=String)
    score = Column(type_=Float)
    ges = Column(type_=Float)
    water = Column(type_=Float)
    page_type = Column(type_=String)
    version = Column(type_=Integer)
