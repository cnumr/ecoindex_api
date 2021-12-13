from typing import Optional
from uuid import UUID

from ecoindex.models import Result
from sqlmodel import Field, SQLModel


class ApiEcoindex(Result, table=True):
    id: Optional[UUID] = Field(
        default=None, description="Analysis ID of type `UUID`", primary_key=True
    )
    host: str = Field(
        default=..., title="Web page host", description="Host name of the web page"
    )
    version: int = Field(
        default=1,
        title="API version",
        description="Version number of the API used to run the test",
    )


class ApiHealth(SQLModel):
    database: bool = Field(default=..., title="Status of database")


example_daily_limit_response = {
    "description": "You have reached the daily limit",
    "content": {
        "application/json": {
            "example": {
                "detail": "You have already reached the daily limit of 5 requests for host www.ecoindex.fr today"
            }
        }
    },
}
