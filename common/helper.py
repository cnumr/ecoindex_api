from common.models import ExceptionResponse


async def format_exception_response(exception: Exception) -> ExceptionResponse:
    return ExceptionResponse(
        exception=type(exception).__name__,
        args=[arg for arg in exception.args if arg] if exception.args else [],
        message=exception.msg if hasattr(exception, "msg") else None,
    )
