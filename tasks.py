from asyncio import run
from os import getcwd

from celery import Celery
from ecoindex_scraper import EcoindexScraper
from ecoindex_scraper.models import ScreenShot, WindowSize

from api.domain.ecoindex.repository import save_ecoindex_result_db
from db.engine import get_session
from settings import (
    ENABLE_SCREENSHOT,
    SCREENSHOTS_GID,
    SCREENSHOTS_UID,
    WAIT_AFTER_SCROLL,
    WAIT_BEFORE_SCROLL,
    WORKER_BACKEND_URL,
    WORKER_BROKER_URL,
)

app = Celery(
    "tasks",
    broker=WORKER_BROKER_URL,
    backend=WORKER_BACKEND_URL,
)


async def session():
    return await get_session().__anext__()


@app.task(name="Make ecoindex analysis", bind=True)
def ecoindex_task(self, url: str, width: int, height: int):
    sql_session = run(session())

    ecoindex = run(
        EcoindexScraper(
            url=url,
            window_size=WindowSize(height=height, width=width),
            wait_after_scroll=WAIT_AFTER_SCROLL,
            wait_before_scroll=WAIT_BEFORE_SCROLL,
            screenshot=ScreenShot(id=str(id), folder=f"{getcwd()}/screenshots/v1")
            if ENABLE_SCREENSHOT
            else None,
            screenshot_gid=SCREENSHOTS_GID,
            screenshot_uid=SCREENSHOTS_UID,
        )
        .init_chromedriver()
        .get_page_analysis()
    )

    db_result = run(
        save_ecoindex_result_db(
            session=sql_session,
            id=self.request.id,
            ecoindex_result=ecoindex,
        )
    )

    return db_result.json()
