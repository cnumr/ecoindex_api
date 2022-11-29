from typing import Any, List

from pydantic import BaseModel


class ExceptionResponse(BaseModel):
    args: List[Any]
    exception: str
    message: str | None
