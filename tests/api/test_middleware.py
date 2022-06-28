import pytest
from db.engine import get_session
from ecoindex_scraper.models import WebPage
from fastapi import HTTPException, Response, status

from api.middleware import validate_analysis_request


@pytest.mark.asyncio
class TestMiddlewareApi:
    async def test_validate_analysis_request_over_quota(self, mocker):
        mocker.patch(
            "api.domain.ecoindex.repository.get_count_daily_request_per_host",
            return_value=10,
        )

        with pytest.raises(HTTPException) as exc:
            await validate_analysis_request(
                Response(),
                get_session(),
                WebPage(url="http://example.com"),
                daily_limit_per_host=10,
            )
        assert exc.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert (
            exc.value.detail
            == "You have already reached the daily limit of 10 requests for host example.com today"
        )

    async def test_validate_analysis_request_under_quota(self, mocker):
        mocker.patch(
            "api.domain.ecoindex.repository.get_count_daily_request_per_host",
            return_value=1,
        )

        await validate_analysis_request(
            Response(),
            get_session(),
            WebPage(url="http://example.com"),
            daily_limit_per_host=10,
        )
