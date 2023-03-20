from json import loads
from typing import Dict
from urllib.parse import urlparse
from uuid import UUID

from celery.result import AsyncResult
from ecoindex.models import WebPage
from fastapi import APIRouter, Path, Response, status
from fastapi.params import Body

from api.domain.task.models.enums import TaskStatus
from api.domain.task.models.examples import (
    example_daily_limit_response,
    example_task_already_in_queue,
)
from api.domain.task.models.response import QueueTaskApi, QueueTaskResult
from common.helper import check_quota
from settings import DAILY_LIMIT_PER_HOST
from worker.tasks import app, ecoindex_task

router = APIRouter()


def get_clean_url(url: str) -> str:
    parsed_url = urlparse(url=url)
    parsed_url.netloc

    return f"{parsed_url.scheme}://{parsed_url.netloc}{parsed_url.path if parsed_url.path else ''}"


def check_task_already_in_queue(url: str, active_tasks_workers: Dict) -> bool:
    for _, active_tasks in active_tasks_workers.items():
        for task in active_tasks:
            if get_clean_url(task["args"][0]) == get_clean_url(url):
                response.status_code = status.HTTP_409_CONFLICT
                response.headers["X-Remaining-Url-Requests"] = str(0)

                return task["id"]


@router.post(
    name="Add new ecoindex analysis task to the waiting queue",
    path="/v1/tasks/ecoindexes",
    response_description="Identifier of the task that has been created in queue",
    responses={
        status.HTTP_201_CREATED: {"model": str},
        status.HTTP_409_CONFLICT: example_task_already_in_queue,
        status.HTTP_429_TOO_MANY_REQUESTS: example_daily_limit_response,
    },
    tags=["Tasks"],
    description="This submits a ecoindex analysis task to the engine",
    status_code=status.HTTP_201_CREATED,
)
async def add_ecoindex_analysis_task(
    response: Response,
    web_page: WebPage = Body(
        default=...,
        title="Web page to analyze defined by its url and its screen resolution",
        example=WebPage(url="https://www.ecoindex.fr", width=1920, height=1080),
    ),
) -> str:
    # Check if task is already in queue

    # Check if already results for this url in the past 6 hours
    # if LIMIT_URL_PER_HOUR:
    #     already_analyzed_url = await check_already_analyzed_url(url=web_page.url)
    #     if already_analyzed_url:
    #         response.status_code = status.HTTP_429_TOO_MANY_REQUESTS
    #         response.headers["X-Remaining-Url-Requests"] = str(0)

    #         return

    def check_task_already_in_queue(active_tasks_workers: Dict) -> bool:
        for _, active_tasks in active_tasks_workers.items():
            for task in active_tasks:
                if get_clean_url(task["args"][0]) == get_clean_url(web_page.url):
                    response.status_code = status.HTTP_409_CONFLICT
                    response.headers["X-Remaining-Url-Requests"] = str(0)

                    return task["id"]

        return None

    active_task = check_task_already_in_queue(app.control.inspect().active())
    if active_task:
        return active_task

    reserved_task = check_task_already_in_queue(app.control.inspect().reserved())
    if reserved_task:
        return reserved_task

    if DAILY_LIMIT_PER_HOST:
        remaining_quota = await check_quota(host=web_page.url.host)
        response.headers["X-Remaining-Daily-Requests"] = str(remaining_quota - 1)

    task_result = ecoindex_task.delay(web_page.url, web_page.width, web_page.height)

    return task_result.id


@router.get(
    name="Get ecoindex analysis task by id",
    path="/v1/tasks/ecoindexes/{id}",
    responses={
        status.HTTP_200_OK: {"model": QueueTaskApi},
        status.HTTP_425_TOO_EARLY: {"model": QueueTaskApi},
    },
    response_description="Get one ecoindex task result by its id",
    tags=["Tasks"],
    description="This returns an ecoindex given by its unique identifier",
)
async def get_ecoindex_analysis_task_by_id(
    response: Response,
    id: UUID = Path(
        default=..., title="Unique identifier of the ecoindex analysis task"
    ),
) -> QueueTaskApi:
    t = AsyncResult(id=str(id), app=app)

    task_response = QueueTaskApi(
        id=t.id,
        status=t.state,
    )

    if t.state == TaskStatus.PENDING:
        response.status_code = status.HTTP_425_TOO_EARLY

        return task_response

    if t.state == TaskStatus.SUCCESS:
        task_response.ecoindex_result = QueueTaskResult(**loads(t.result))

    if t.state == TaskStatus.FAILURE:
        task_response.task_error = t.info

    response.status_code = status.HTTP_200_OK

    return task_response


@router.delete(
    name="Abort ecoindex analysis by id",
    path="/v1/tasks/ecoindexes/{id}",
    response_description="Abort one ecoindex task by its id if it is still waiting",
    tags=["Tasks"],
    description="This aborts one ecoindex task by its id if it is still waiting",
)
async def get_ecoindex_analysis_task_by_id(
    id: UUID = Path(
        default=..., title="Unique identifier of the ecoindex analysis task"
    ),
) -> None:
    res = app.control.revoke(id, terminate=True, signal="SIGKILL")

    return res
