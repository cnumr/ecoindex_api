from json import loads
from uuid import UUID

from celery.result import AsyncResult
from ecoindex.models import WebPage
from fastapi import APIRouter, Path, Response, status
from fastapi.params import Body

from api.domain.task.models.enums import TaskStatus
from api.domain.task.models.examples import example_daily_limit_response
from api.domain.task.models.response import QueueTaskApi, QueueTaskResult
from common.helper import check_quota
from settings import DAILY_LIMIT_PER_HOST
from worker.tasks import app, ecoindex_task

router = APIRouter()


@router.post(
    name="Add new ecoindex analysis task to the waiting queue",
    path="/v1/tasks/ecoindexes",
    response_description="Identifier of the task that has been created in queue",
    responses={
        status.HTTP_201_CREATED: {"model": str},
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
