from datetime import date
from os import getcwd
from uuid import UUID

from api.application.middleware.analysis import validate_analysis_request
from api.application.status import (
    HTTP_520_ECOINDEX_TYPE_ERROR,
    HTTP_521_ECOINDEX_CONNECTION_ERROR,
)
from api.domain.ecoindex.models.examples import (
    example_daily_limit_response,
    example_ecoindex_not_found,
)
from api.domain.ecoindex.models.responses import ApiEcoindex, PageApiEcoindexes
from api.domain.ecoindex.repository import (
    get_count_analysis_db,
    get_ecoindex_result_by_id_db,
    get_ecoindex_result_list_db,
    save_ecoindex_result_db,
)
from api.helper import get_status_code, new_uuid
from api.models.enums import Version
from api.models.examples import (
    example_exception_ERR_CONNECTION_TIMED_OUT_response,
    example_exception_ERR_NAME_NOT_RESOLVED_response,
    example_exception_HTTP_520_ECOINDEX_TYPE_ERROR_response,
    example_exception_HTTP_521_ECOINDEX_CONNECTION_ERROR_response,
    example_exception_response,
    example_file_not_found,
)
from db.engine import get_session
from ecoindex_scraper import EcoindexScraper
from ecoindex_scraper.models import ScreenShot, WebPage, WindowSize
from fastapi import APIRouter, Response, status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Path
from fastapi.params import Body, Depends, Query
from fastapi.responses import FileResponse
from settings import (
    DAILY_LIMIT_PER_HOST,
    ENABLE_SCREENSHOT,
    SCREENSHOTS_GID,
    SCREENSHOTS_UID,
    WAIT_AFTER_SCROLL,
    WAIT_BEFORE_SCROLL,
)
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()


@router.post(
    name="New ecoindex analysis",
    path="/v1/ecoindexes",
    response_model=ApiEcoindex,
    response_description="Corresponding ecoindex result",
    responses={
        status.HTTP_429_TOO_MANY_REQUESTS: example_daily_limit_response,
        status.HTTP_500_INTERNAL_SERVER_ERROR: example_exception_response,
        status.HTTP_502_BAD_GATEWAY: example_exception_ERR_NAME_NOT_RESOLVED_response,
        status.HTTP_504_GATEWAY_TIMEOUT: example_exception_ERR_CONNECTION_TIMED_OUT_response,
        HTTP_520_ECOINDEX_TYPE_ERROR: example_exception_HTTP_520_ECOINDEX_TYPE_ERROR_response,
        HTTP_521_ECOINDEX_CONNECTION_ERROR: example_exception_HTTP_521_ECOINDEX_CONNECTION_ERROR_response,
    },
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
    await validate_analysis_request(
        response=response,
        session=session,
        web_page=web_page,
        daily_limit_per_host=DAILY_LIMIT_PER_HOST,
    )

    id = await new_uuid()

    web_page_result = (
        await EcoindexScraper(
            url=web_page.url,
            window_size=WindowSize(height=web_page.height, width=web_page.width),
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

    return await save_ecoindex_result_db(
        session=session, id=id, ecoindex_result=web_page_result
    )


@router.get(
    name="Get ecoindex analysis list",
    path="/{version}/ecoindexes",
    response_model=PageApiEcoindexes,
    response_description="List of corresponding ecoindex results",
    responses={
        status.HTTP_206_PARTIAL_CONTENT: {"model": PageApiEcoindexes},
        status.HTTP_404_NOT_FOUND: {"model": PageApiEcoindexes},
    },
    tags=["Ecoindex"],
    description=(
        "This returns a list of ecoindex analysis "
        "corresponding to query filters and the given version engine. "
        "The results are ordered by ascending date"
    ),
)
async def get_ecoindex_analysis_list(
    response: Response,
    session: AsyncSession = Depends(get_session),
    version: Version = Path(
        default=...,
        title="Engine version",
        description="Engine version used to run the analysis (v0 or v1)",
        example=Version.v1.value,
    ),
    date_from: date
    | None = Query(
        None, description="Start date of the filter elements (example: 2020-01-01)"
    ),
    date_to: date
    | None = Query(
        None, description="End date of the filter elements  (example: 2020-01-01)"
    ),
    host: str | None = Query(None, description="Host name you want to filter"),
    page: int | None = Query(1, description="Page number", ge=1),
    size: int
    | None = Query(50, description="Number of elements per page", ge=1, le=100),
) -> PageApiEcoindexes:
    ecoindexes = await get_ecoindex_result_list_db(
        session=session,
        date_from=date_from,
        date_to=date_to,
        host=host,
        version=version,
        page=page,
        size=size,
    )
    total_results = await get_count_analysis_db(
        session=session,
        version=version,
        date_from=date_from,
        date_to=date_to,
        host=host,
    )

    response.status_code = await get_status_code(items=ecoindexes, total=total_results)

    return PageApiEcoindexes(
        items=ecoindexes, total=total_results, page=page, size=size
    )


@router.get(
    name="Get ecoindex analysis by id",
    path="/{version}/ecoindexes/{id}",
    response_model=ApiEcoindex,
    response_description="Get one ecoindex result by its id",
    responses={status.HTTP_404_NOT_FOUND: example_ecoindex_not_found},
    tags=["Ecoindex"],
    description="This returns an ecoindex given by its unique identifier",
)
async def get_ecoindex_analysis_by_id(
    session: AsyncSession = Depends(get_session),
    version: Version = Path(
        default=...,
        title="Engine version",
        description="Engine version used to run the analysis (v0 or v1)",
        example=Version.v1.value,
    ),
    id: UUID = Path(default=..., title="Unique identifier of the ecoindex analysis"),
) -> ApiEcoindex:
    ecoindex = await get_ecoindex_result_by_id_db(
        session=session, id=id, version=version
    )
    if not ecoindex:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Analysis {id} not found for version {version.value}",
        )
    return ecoindex


@router.get(
    name="Get screenshot",
    path="/{version}/ecoindexes/{id}/screenshot",
    tags=["Ecoindex"],
    description="This returns the screenshot of the webpage analysis if it exists",
    responses={status.HTTP_404_NOT_FOUND: example_file_not_found},
)
async def get_screenshot(
    version: Version = Path(
        default=...,
        title="Engine version",
        description="Engine version used to run the analysis (v0 or v1)",
        example=Version.v1.value,
    ),
    id: UUID = Path(default=..., title="Unique identifier of the ecoindex analysis"),
):
    return FileResponse(
        path=f"{getcwd()}/screenshots/{version}/{id}.webp",
        filename=f"{id}.webp",
        content_disposition_type="inline",
        media_type="image/webp",
    )
