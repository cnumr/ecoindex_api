from typing import Optional

from ecoindex.models import Result
from pydantic.fields import Field
from pydantic.types import UUID4


class ApiResult(Result):
    id: Optional[UUID4] = Field(default=None, description="Analysis ID")
    host: str = Field(
        default=..., title="Web page host", description="Host name of the web page"
    )
    version: int = Field(
        default=1,
        title="API version",
        description="Version number of the API used to run the test",
    )

    class Config:
        orm_mode = True
