from typing import Any

from pydantic import BaseModel, Field


class QueueTaskError(BaseModel):
    exception: str = Field(default=..., title="Name of the exception that was raised")
    message: str = Field(default=..., title="Message of the exception")
    detail: Any | None = Field(
        default=None, title="Detail object of the raised exception"
    )


class QueueTask(BaseModel):
    id: str = Field(
        default=...,
        title="Identifier of the current. This identifier will become the identifier of the analysis",
    )
    status: str = Field(
        default=...,
        title="Status of the current task. Can be PENDING, SCHEDULED, ACTIVE, RESERVED, FAILURE",
    )
    detail: QueueTaskError | None = Field(default=None, title="Detail of the analysis")
