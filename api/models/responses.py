from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class ApiHealth(SQLModel):
    database: bool = Field(default=..., title="Status of database")


class ExceptionResponse(BaseModel):
    args: List[Any]
    exception: str
    message: Optional[str]
