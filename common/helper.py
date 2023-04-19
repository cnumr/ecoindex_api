from json import loads

import api
from common.exception import QuotaExceededException
from common.models import ExceptionResponse
from settings import Settings


async def format_exception_response(exception: Exception) -> ExceptionResponse:
    return ExceptionResponse(
        exception=type(exception).__name__,
        args=[arg for arg in exception.args if arg] if exception.args else [],
        message=exception.msg if hasattr(exception, "msg") else None,
    )


async def check_quota(
    host: str,
) -> int | None:
    if not Settings().DAILY_LIMIT_PER_HOST:
        return

    count_daily_request_per_host = (
        await api.domain.ecoindex.repository.get_count_daily_request_per_host(host=host)
    )

    if count_daily_request_per_host >= Settings().DAILY_LIMIT_PER_HOST:
        latest_result = await api.domain.ecoindex.repository.get_latest_result(
            host=host
        )
        raise QuotaExceededException(
            limit=Settings().DAILY_LIMIT_PER_HOST,
            host=host,
            latest_result=loads(latest_result.json()),
        )

    return Settings().DAILY_LIMIT_PER_HOST - count_daily_request_per_host
