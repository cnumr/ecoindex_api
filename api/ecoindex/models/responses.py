from typing import List, Optional
from uuid import UUID

from ecoindex.models import Result
from pydantic import BaseModel
from sqlmodel import Field


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


class PageApiEcoindexes(BaseModel):
    items: List[ApiEcoindex]
    total: int
    page: int
    size: int
    next_page: int
    first_page: int
    previous_page: int
    last_page: int
