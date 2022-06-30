import pytest
from api.domain.health.chromedriver import is_chromedriver_healthy
from ecoindex_scraper.models import Result
from selenium.common.exceptions import WebDriverException


@pytest.mark.asyncio
class TestChromedriverHealth:
    async def test_validate_chromedriver_is_healthy(self, mocker):
        mocker.patch(
            "ecoindex_scraper.get_page_analysis",
            return_value=Result(
                width=1920,
                height=1080,
                url="https://www.google.com",
                date="2020-01-01 00:00:00",
                ges=1.0,
                water=1.0,
                requests=1,
                nodes=100,
                size=1,
                grade="A",
                score=100,
                page_type=None,
            ),
        )

        chromedriver_healthy = await is_chromedriver_healthy()
        assert chromedriver_healthy == {"chromedriver": True}

    async def test_validate_chromedriver_is_unhealthy(self, mocker):
        mocker.patch(
            "ecoindex_scraper.get_page_analysis",
            side_effect=WebDriverException(
                "This version of ChromeDriver only supports Chrome version"
            ),
        )

        chromedriver_healthy = await is_chromedriver_healthy()
        assert chromedriver_healthy == {"chromedriver": False}
