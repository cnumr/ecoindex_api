from uuid import UUID, uuid4

from api.models.responses import ExceptionResponse


def format_exception_response(exception: Exception) -> ExceptionResponse:
    return ExceptionResponse(
        exception=type(exception).__name__,
        args=[arg for arg in exception.args if arg] if exception.args else [],
        message=exception.msg if hasattr(exception, "msg") else None,
    )


def new_uuid() -> UUID:
    val = uuid4()
    while val.hex[0] == "0":
        val = uuid4()
    return val
