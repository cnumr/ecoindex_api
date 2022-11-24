from json import loads
from uuid import UUID

from celery.result import AsyncResult
from ecoindex.models import WebPage
from fastapi import APIRouter, Path, Response, status
from fastapi.params import Body, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from api.application.middleware.analysis import validate_analysis_request
from api.domain.task.models.response import QueueTaskApi, QueueTaskResult
from db.engine import get_session
from settings import DAILY_LIMIT_PER_HOST
from worker.tasks import app, ecoindex_task

router = APIRouter()


@router.post(
    name="Add new ecoindex analysis task to the waiting queue",
    path="/v1/tasks/ecoindexes",
    response_description="Identifier of the task that has been created in queue",
    tags=["Tasks"],
    description="This submits a ecoindex analysis task to the engine",
    status_code=status.HTTP_201_CREATED,
)
async def add_ecoindex_analysis_task(
    response: Response,
    session: AsyncSession = Depends(get_session),
    web_page: WebPage = Body(
        default=...,
        title="Web page to analyze defined by its url and its screen resolution",
        example=WebPage(url="http://www.ecoindex.fr", width=1920, height=1080),
    ),
) -> str:
    await validate_analysis_request(
        response=response,
        session=session,
        web_page=web_page,
        daily_limit_per_host=DAILY_LIMIT_PER_HOST,
    )

    task_result = ecoindex_task.delay(web_page.url, web_page.width, web_page.height)

    return task_result.id


@router.get(
    name="Get ecoindex analysis task by id",
    path="/v1/tasks/ecoindexes/{id}",
    response_model=QueueTaskApi,
    response_description="Get one ecoindex task result by its id",
    tags=["Tasks"],
    description="This returns an ecoindex given by its unique identifier",
)
async def get_ecoindex_analysis_task_by_id(
    id: UUID = Path(
        default=..., title="Unique identifier of the ecoindex analysis task"
    ),
) -> QueueTaskApi:
    t = AsyncResult(id=str(id), app=app)

    response = QueueTaskApi(
        id=t.id,
        status=t.state,
    )

    if t.state == "SUCCESS":
        response.ecoindex_result = QueueTaskResult(**loads(t.result))

    if t.state == "FAILURE":
        response.task_error = t.info

    return response


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
