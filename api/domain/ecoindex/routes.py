from datetime import date
from os import getcwd
from uuid import UUID

from fastapi import APIRouter, Response, status
from fastapi.exceptions import HTTPException
from fastapi.param_functions import Path
from fastapi.params import Query
from fastapi.responses import FileResponse

from api.domain.ecoindex.models.examples import example_ecoindex_not_found
from api.domain.ecoindex.models.responses import ApiEcoindex, PageApiEcoindexes
from api.domain.ecoindex.repository import (
    get_count_analysis_db,
    get_ecoindex_result_by_id_db,
    get_ecoindex_result_list_db,
)
from api.helper import get_status_code
from api.models.enums import Version
from api.models.examples import example_file_not_found

router = APIRouter()


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
        date_from=date_from,
        date_to=date_to,
        host=host,
        version=version,
        page=page,
        size=size,
    )
    total_results = await get_count_analysis_db(
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
    version: Version = Path(
        default=...,
        title="Engine version",
        description="Engine version used to run the analysis (v0 or v1)",
        example=Version.v1.value,
    ),
    id: UUID = Path(default=..., title="Unique identifier of the ecoindex analysis"),
) -> ApiEcoindex:
    ecoindex = await get_ecoindex_result_by_id_db(id=id, version=version)

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
