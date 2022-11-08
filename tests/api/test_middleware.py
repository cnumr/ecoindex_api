import pytest
from db.engine import get_session
from ecoindex_scraper.models import WebPage
from fastapi import HTTPException, Response, status

from api.application.middleware.analysis import validate_analysis_request


@pytest.mark.asyncio
class TestMiddlewareApi:
    async def test_validate_analysis_request_over_quota(self, mocker):
        mocker.patch(
            "api.domain.ecoindex.repository.get_count_daily_request_per_host",
            return_value=5,
        )

        with pytest.raises(HTTPException) as exc:
            await validate_analysis_request(
                Response(),
                get_session(),
                WebPage(url="http://example.com"),
                daily_limit_per_host=5,
            )
        assert exc.value.status_code == status.HTTP_429_TOO_MANY_REQUESTS
        assert (
            exc.value.detail["message"]
            == "You have already reached the daily limit of 5 requests for host example.com today"
        )
        assert exc.value.detail["daily_limit_per_host"] == 5
        assert exc.value.detail["host"] == "example.com"

    async def test_validate_analysis_request_under_quota(self, mocker):
        mocker.patch(
            "api.domain.ecoindex.repository.get_count_daily_request_per_host",
            return_value=1,
        )

        await validate_analysis_request(
            Response(),
            get_session(),
            WebPage(url="http://example.com"),
            daily_limit_per_host=5,
        )
