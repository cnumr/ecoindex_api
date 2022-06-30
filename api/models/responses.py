from typing import Any, List, Optional

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class ApiHealth(SQLModel):
    database: bool = Field(default=..., title="Status of database")
    chromedriver: bool = Field(default=..., title="Status of chromedriver")


class ExceptionResponse(BaseModel):
    args: List[Any]
    exception: str
    message: Optional[str]
