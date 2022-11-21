from sqlmodel import Field, SQLModel


class QueueTask(SQLModel):
    id: str = Field(
        default=...,
        title="Identifier of the current. This identifier will become the identifier of the analysis",
    )
    status: str = Field(
        default=...,
        title="Status of the current task. Can be PENDING, SCHEDULED, ACTIVE, RESERVED, ",
    )
