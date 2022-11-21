from sqlmodel import Field, SQLModel


class ApiHealth(SQLModel):
    database: bool = Field(default=..., title="Status of database")
    chromedriver: bool = Field(default=..., title="Status of chromedriver")
