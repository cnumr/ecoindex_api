from typing import Any, List

from sqlmodel import Field, SQLModel


class ApiHealth(SQLModel):
    database: bool = Field(default=..., title="Status of database")
    worker: List[Any] = Field(default=..., title="Status of the queue task broker")
