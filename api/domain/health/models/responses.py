from typing import List

from pydantic import BaseModel
from sqlmodel import Field, SQLModel


class WorkerHealth(BaseModel):
    name: str = Field(default=..., title="Name of the worker")
    healthy: bool = Field(
        default=..., title="Set to true if the worker is healthy, else false"
    )


class WorkersHealth(BaseModel):
    healthy: bool = Field(
        default=...,
        title="Set to true if all workers are healthy, false if one of them is down",
    )
    workers: List[WorkerHealth] = Field(
        default=..., title="List of all current known workers"
    )


class ApiHealth(SQLModel):
    database: bool = Field(default=..., title="Status of database")
    workers: WorkersHealth = Field(default=..., title="Status of the queue task broker")
