from datetime import date
from typing import Optional
from uuid import UUID

from api.models import (
    ApiEcoindex,
    example_daily_limit_response,
    example_exception_response,
)
from db.crud import (
    get_count_daily_request_per_host,
    get_ecoindex_result_by_id_db,
    get_ecoindex_result_list_db,
    save_ecoindex_result_db,
)
from db.database import get_session
from fastapi import APIRouter, Response, status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Path
from fastapi.params import Body, Depends, Query
from fastapi_pagination import Page, paginate
from settings import DAILY_LIMIT_PER_HOST
from sqlmodel.ext.asyncio.session import AsyncSession

from ecoindex import get_page_analysis
from ecoindex.models import WebPage, WindowSize

router = APIRouter()


@router.post(
    path="/v1/ecoindexes",
    response_model=ApiEcoindex,
    response_description="Corresponding ecoindex result",
    responses={429: example_daily_limit_response, 500: example_exception_response},
    tags=["Ecoindex"],
    description="This performs ecoindex analysis of a given webpage with a defined resolution",
    status_code=status.HTTP_201_CREATED,
)
async def add_ecoindex_analysis(
    response: Response,
    session: AsyncSession = Depends(get_session),
    web_page: WebPage = Body(
        default=...,
        title="Web page to analyze defined by its url and its screen resolution",
        example=WebPage(url="http://www.ecoindex.fr", width=1920, height=1080),
    ),
) -> ApiEcoindex:
    if DAILY_LIMIT_PER_HOST:
        count_daily_request_per_host = await get_count_daily_request_per_host(
            session=session, host=web_page.url.host
        )
        response.headers["X-Remaining-Daily-Requests"] = str(
            DAILY_LIMIT_PER_HOST - count_daily_request_per_host - 1
        )

    if DAILY_LIMIT_PER_HOST and count_daily_request_per_host >= DAILY_LIMIT_PER_HOST:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=(
                f"You have already reached the daily limit of "
                f"{DAILY_LIMIT_PER_HOST} requests for host {web_page.url.host} today"
            ),
        )

    web_page_result = await get_page_analysis(
        url=web_page.url,
        window_size=WindowSize(height=web_page.height, width=web_page.width),
        wait_before_scroll=3,
        wait_after_scroll=3,
    )

    db_result = await save_ecoindex_result_db(
        session=session, ecoindex_result=web_page_result
    )

    return db_result


@router.get(
    path="/v1/ecoindexes",
    response_model=Page[ApiEcoindex],
    response_description="List of corresponding ecoindex results",
    responses={500: example_exception_response},
    tags=["Ecoindex"],
    description=(
        "This returns a list of ecoindex analysis "
        "corresponding to query filters. "
        "The results are ordered by ascending date"
    ),
)
async def get_ecoindex_analysis_list(
    session: AsyncSession = Depends(get_session),
    date_from: Optional[date] = Query(
        None, description="Start date of the filter elements (example: 2020-01-01)"
    ),
    date_to: Optional[date] = Query(
        None, description="End date of the filter elements  (example: 2020-01-01)"
    ),
    host: Optional[str] = Query(None, description="Host name you want to filter"),
) -> Page[ApiEcoindex]:
    ecoindexes = await get_ecoindex_result_list_db(
        session=session, date_from=date_from, date_to=date_to, host=host
    )

    return paginate(ecoindexes)


@router.get(
    path="/v1/ecoindexes/{id}",
    response_model=ApiEcoindex,
    response_description="Get one ecoindex result by its id",
    responses={500: example_exception_response},
    tags=["Ecoindex"],
    description="This returns an ecoindex given by its unique identifier",
)
async def get_ecoindex_analysis_by_id(
    session: AsyncSession = Depends(get_session),
    id: UUID = Path(default=..., title="Unique identifier of the ecoindex analysis"),
) -> ApiEcoindex:
    ecoindex = await get_ecoindex_result_by_id_db(session=session, id=id)
    if not ecoindex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis {id} not found",
        )
    return ecoindex
