from asyncio import run
from os import getcwd

from celery import Celery
from ecoindex.models import ScreenShot, WindowSize
from ecoindex_scraper import EcoindexScraper
from selenium.common.exceptions import WebDriverException

from api.domain.ecoindex.repository import save_ecoindex_result_db
from api.domain.task.models.response import QueueTaskError, QueueTaskResult
from common.helper import format_exception_response
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
from worker.exceptions import (
    EcoindexContentTypeError,
    EcoindexHostUnreachable,
    EcoindexPageNotFound,
    EcoindexStatusError,
    EcoindexTimeout,
)

app: Celery = Celery(
    "tasks",
    broker=WORKER_BROKER_URL,
    backend=WORKER_BACKEND_URL,
)


async def session():
    return await get_session().__anext__()


@app.task(name="Make ecoindex analysis", bind=True)
def ecoindex_task(self, url: str, width: int, height: int):
    sql_session = run(session())
    try:
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

        return QueueTaskResult(status="SUCCESS", detail=db_result).json()

    except WebDriverException as exc:
        if "ERR_NAME_NOT_RESOLVED" in exc.msg:
            return QueueTaskResult(
                status="FAILURE",
                error=QueueTaskError(
                    url=url,
                    exception=EcoindexHostUnreachable.__name__,
                    status_code=502,
                    message="This host is unreachable (error 502). Are you really sure of this url? 🤔",
                    detail=None,
                ),
            ).json()

        if "ERR_CONNECTION_TIMED_OUT" in exc.msg:
            return QueueTaskResult(
                status="FAILURE",
                error=QueueTaskError(
                    url=url,
                    exception=EcoindexTimeout.__name__,
                    status_code=504,
                    message="Timeout reached when requesting this url (error 504). This is probably a temporary issue. 😥",
                    detail=None,
                ),
            ).json()

        return QueueTaskResult(
            status="FAILURE",
            error=QueueTaskError(
                url=url,
                exception=type(exc).__name__,
                status_code=500,
                message=exc.msg,
                detail=run(format_exception_response(exception=exc)),
            ),
        ).json()

    except TypeError as exc:
        error = exc.args[0]

        return QueueTaskResult(
            status="FAILURE",
            error=QueueTaskError(
                url=url,
                exception=EcoindexContentTypeError.__name__,
                status_code=520,
                message=error["message"],
                detail={"mimetype": error["mimetype"]},
            ),
        ).json()

    except ConnectionError as exc:
        error = exc.args[0]

        return QueueTaskResult(
            status="FAILURE",
            error=QueueTaskError(
                url=url,
                status_code=521,
                exception=EcoindexStatusError.__name__,
                message=error["message"],
                detail={"status": error["status"]},
            ),
        ).json()
