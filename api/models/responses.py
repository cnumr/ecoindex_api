from sqlmodel import Field, SQLModel


class ApiHealth(SQLModel):
    database: bool = Field(default=..., title="Status of database")
    worker: bool = Field(default=..., title="Status of the queue task broker")
