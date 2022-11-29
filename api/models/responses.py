from typing import Dict, List

from sqlmodel import Field, SQLModel


class ApiHealth(SQLModel):
    database: bool = Field(default=..., title="Status of database")
    workers: List[Dict] = Field(default=..., title="Status of the queue task broker")
