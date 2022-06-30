import ecoindex_scraper
from ecoindex_scraper.models import WebPage, WindowSize
from selenium.common.exceptions import WebDriverException


async def is_chromedriver_healthy():
    try:
        web_page = WebPage(width=1920, height=1080, url="https://www.google.com")
        await ecoindex_scraper.get_page_analysis(
            url=web_page.url,
            window_size=WindowSize(height=web_page.height, width=web_page.width),
            wait_before_scroll=0,
            wait_after_scroll=0,
        )
    except WebDriverException as e:
        if "This version of ChromeDriver only supports Chrome version" in e.msg:
            return {"chromedriver": False}

    return {"chromedriver": True}
