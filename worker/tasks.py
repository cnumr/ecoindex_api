from asyncio import run
from os import getcwd
from urllib.parse import urlparse

from celery import Celery
from ecoindex.models import ScreenShot, WindowSize
from ecoindex_scraper import EcoindexScraper
from selenium.common.exceptions import WebDriverException

from api.domain.task.models.enums import TaskStatus
from api.domain.task.models.response import QueueTaskError, QueueTaskResult
from common.exception import QuotaExceededException
from common.helper import check_quota, format_exception_response
from settings import (
    CHROME_VERSION_MAIN,
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
    EcoindexStatusError,
    EcoindexTimeout,
)
from worker.repository import save_ecoindex_result_db

app: Celery = Celery(
    "tasks",
    broker=WORKER_BROKER_URL,
    backend=WORKER_BACKEND_URL,
)


@app.task(
    name="Make ecoindex analysis",
    bind=True,
    autoretry_for=(Exception,),
    retry_backoff=5,
    retry_kwargs={"max_retries": 5},
)
def ecoindex_task(self, url: str, width: int, height: int) -> str:
    queue_task_result = run(async_ecoindex_task(self, url, width, height))

    return queue_task_result.json()


async def async_ecoindex_task(
    self, url: str, width: int, height: int
) -> QueueTaskResult:
    try:
        await check_quota(host=urlparse(url=url).netloc)

        ecoindex = await (
            EcoindexScraper(
                url=url,
                chrome_version_main=CHROME_VERSION_MAIN,
                window_size=WindowSize(height=height, width=width),
                wait_after_scroll=WAIT_AFTER_SCROLL,
                wait_before_scroll=WAIT_BEFORE_SCROLL,
                screenshot=ScreenShot(
                    id=str(self.request.id), folder=f"{getcwd()}/screenshots/v1"
                )
                if ENABLE_SCREENSHOT
                else None,
                screenshot_gid=SCREENSHOTS_GID,
                screenshot_uid=SCREENSHOTS_UID,
            )
            .init_chromedriver()
            .get_page_analysis()
        )

        db_result = await (
            save_ecoindex_result_db(
                id=self.request.id,
                ecoindex_result=ecoindex,
            )
        )

        return QueueTaskResult(status=TaskStatus.SUCCESS, detail=db_result)

    except QuotaExceededException as exc:
        return QueueTaskResult(
            status=TaskStatus.FAILURE,
            error=QueueTaskError(
                url=url,
                exception=QuotaExceededException.__name__,
                status_code=429,
                message=exc.message,
                detail=exc.__dict__,
            ),
        )

    except WebDriverException as exc:
        if "ERR_NAME_NOT_RESOLVED" in exc.msg:
            return QueueTaskResult(
                status=TaskStatus.FAILURE,
                error=QueueTaskError(
                    url=url,
                    exception=EcoindexHostUnreachable.__name__,
                    status_code=502,
                    message="This host is unreachable (error 502). Are you really sure of this url? 🤔",
                    detail=None,
                ),
            )

        if "ERR_CONNECTION_TIMED_OUT" in exc.msg:
            return QueueTaskResult(
                status=TaskStatus.FAILURE,
                error=QueueTaskError(
                    url=url,
                    exception=EcoindexTimeout.__name__,
                    status_code=504,
                    message="Timeout reached when requesting this url (error 504). This is probably a temporary issue. 😥",
                    detail=None,
                ),
            )

        return QueueTaskResult(
            status=TaskStatus.FAILURE,
            error=QueueTaskError(
                url=url,
                exception=type(exc).__name__,
                status_code=500,
                message=exc.msg,
                detail=await format_exception_response(exception=exc),
            ),
        )

    except TypeError as exc:
        error = exc.args[0]

        return QueueTaskResult(
            status=TaskStatus.FAILURE,
            error=QueueTaskError(
                url=url,
                exception=EcoindexContentTypeError.__name__,
                status_code=520,
                message=error["message"],
                detail={"mimetype": error["mimetype"]},
            ),
        )

    except ConnectionError as exc:
        error = exc.args[0]

        return QueueTaskResult(
            status=TaskStatus.FAILURE,
            error=QueueTaskError(
                url=url,
                status_code=521,
                exception=EcoindexStatusError.__name__,
                message=error["message"],
                detail={"status": error["status"]},
            ),
        )
