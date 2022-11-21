from uuid import UUID

from celery.result import AsyncResult
from ecoindex_scraper.models import WebPage
from fastapi import APIRouter, Path, Response, status
from fastapi.params import Body, Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from api.application.middleware.analysis import validate_analysis_request
from api.domain.task.models.examples import example_ecoindex_task_not_found
from api.domain.task.models.response import QueueTask
from db.engine import get_session
from settings import DAILY_LIMIT_PER_HOST
from worker.tasks import app, ecoindex_task

router = APIRouter()


@router.post(
    name="Add new ecoindex analysis task to the waiting queue",
    path="/ecoindexes/tasks",
    response_model=QueueTask,
    response_description="Information about the task that has been created in queue",
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
) -> QueueTask:
    await validate_analysis_request(
        response=response,
        session=session,
        web_page=web_page,
        daily_limit_per_host=DAILY_LIMIT_PER_HOST,
    )

    result = ecoindex_task.delay(web_page.url, web_page.width, web_page.height)

    return result


@router.get(
    name="Get ecoindex analysis task by id",
    path="/ecoindexes/tasks/{id}",
    response_model=QueueTask,
    response_description="Get one ecoindex task result by its id",
    responses={status.HTTP_404_NOT_FOUND: example_ecoindex_task_not_found},
    tags=["Tasks"],
    description="This returns an ecoindex given by its unique identifier",
)
async def get_ecoindex_analysis_task_by_id(
    id: UUID = Path(
        default=..., title="Unique identifier of the ecoindex analysis task"
    ),
) -> QueueTask:
    res = AsyncResult(id=str(id), app=app)

    return res
