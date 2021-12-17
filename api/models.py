from typing import Any, List, Optional
from uuid import UUID

from ecoindex.models import Result
from pydantic.main import BaseModel
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


class ExceptionResponse(BaseModel):
    args: List[Any]
    exception: str
    message: Optional[str]


example_exception_response = {
    "description": "My bad! :( => Server exception",
    "content": {
        "application/json": {
            "example": {
                "detail": {
                    "args": [
                        "unknown error: net::ERR_NAME_NOT_RESOLVED\n  (Session info: headless chrome=96.0.4664.110)",
                        [
                            "#0 0x55ffa3dd7ee3 <unknown>",
                            "#1 0x55ffa38a5608 <unknown>",
                        ],
                    ],
                    "exception": "WebDriverException",
                    "message": "unknown error: net::ERR_NAME_NOT_RESOLVED\n  (Session info: headless chrome=96.0.4664.110)",
                }
            }
        }
    },
}
