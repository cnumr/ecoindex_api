import api
from common.exception import QuotaExceededException
from common.models import ExceptionResponse
from settings import DAILY_LIMIT_PER_HOST


async def format_exception_response(exception: Exception) -> ExceptionResponse:
    return ExceptionResponse(
        exception=type(exception).__name__,
        args=[arg for arg in exception.args if arg] if exception.args else [],
        message=exception.msg if hasattr(exception, "msg") else None,
    )


async def check_quota(
    host: str,
) -> int | None:
    if not DAILY_LIMIT_PER_HOST:
        return

    count_daily_request_per_host = (
        await api.domain.ecoindex.repository.get_count_daily_request_per_host(host=host)
    )

    if count_daily_request_per_host >= DAILY_LIMIT_PER_HOST:
        raise QuotaExceededException(limit=DAILY_LIMIT_PER_HOST, host=host)

    return DAILY_LIMIT_PER_HOST - count_daily_request_per_host
