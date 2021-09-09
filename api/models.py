from typing import Optional
from uuid import UUID

from ecoindex.models import Result
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
