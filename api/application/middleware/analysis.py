from ecoindex.models import WebPage
from fastapi import HTTPException, Response, status
from sqlmodel.ext.asyncio.session import AsyncSession

import api.domain.ecoindex.repository


async def validate_analysis_request(
    response: Response,
    session: AsyncSession,
    web_page: WebPage,
    daily_limit_per_host: int,
) -> None:
    if daily_limit_per_host:
        count_daily_request_per_host = (
            await api.domain.ecoindex.repository.get_count_daily_request_per_host(
                session=session, host=web_page.url.host
            )
        )
        response.headers["X-Remaining-Daily-Requests"] = str(
            daily_limit_per_host - count_daily_request_per_host - 1
        )

    if daily_limit_per_host and count_daily_request_per_host >= daily_limit_per_host:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "message": (
                    "You have already reached the daily limit of "
                    f"{daily_limit_per_host} requests for host {web_page.url.host} today"
                ),
                "daily_limit_per_host": daily_limit_per_host,
                "host": web_page.url.host,
            },
        )
