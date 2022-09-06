from unittest.mock import patch

import pytest
from api.domain.health.chromedriver import is_chromedriver_healthy
from ecoindex_scraper import EcoindexScraper
from selenium.common.exceptions import WebDriverException


@pytest.mark.asyncio
class TestChromedriverHealth:
    @patch.object(EcoindexScraper, "init_chromedriver")
    async def test_validate_chromedriver_is_healthy(self, mock_init_chromedriver):
        chromedriver_healthy = await is_chromedriver_healthy()

        mock_init_chromedriver.assert_called()
        assert chromedriver_healthy == {"chromedriver": True}

    @patch.object(EcoindexScraper, "init_chromedriver")
    async def test_validate_chromedriver_is_unhealthy(self, mock_init_chromedriver):
        mock_init_chromedriver.side_effect = WebDriverException(
            "unknown error: cannot connect to chrome at 127.0.0.1:52327 from session not created: This version of ChromeDriver only supports Chrome version 103 Current browser version is 102.0.5005.61"
        )

        chromedriver_healthy = await is_chromedriver_healthy()

        mock_init_chromedriver.assert_called()
        assert chromedriver_healthy == {"chromedriver": False}
