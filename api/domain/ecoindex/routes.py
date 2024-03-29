from datetime import date
from os import getcwd
from typing import Annotated
from uuid import UUID

from ecoindex import get_ecoindex
from ecoindex.models import Ecoindex
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
from api.helper import get_sort_parameters, get_status_code
from api.models.enums import Version
from api.models.examples import example_file_not_found

router = APIRouter()


@router.get(
    name="Compute ecoindex",
    path="/ecoindex",
    tags=["Ecoindex"],
    description=(
        "This returns the ecoindex computed based on the given parameters: "
        "DOM (number of DOM nodes), size (total size in Kb) and requests"
    ),
)
async def compute_ecoindex(
    dom: Annotated[
        int,
        Query(
            default=...,
            description="Number of DOM nodes of the page",
            gt=0,
            example=204,
        ),
    ],
    size: Annotated[
        float,
        Query(
            default=..., description="Total size of the page in Kb", gt=0, example=109
        ),
    ],
    requests: Annotated[
        int,
        Query(
            default=..., description="Number of requests of the page", gt=0, example=5
        ),
    ],
) -> Ecoindex:
    return await get_ecoindex(dom=dom, size=size, requests=requests)


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
    date_from: Annotated[
        date | None,
        Query(description="Start date of the filter elements (example: 2020-01-01)"),
    ] = None,
    date_to: Annotated[
        date | None,
        Query(description="End date of the filter elements  (example: 2020-01-01)"),
    ] = None,
    host: Annotated[
        str | None, Query(description="Host name you want to filter")
    ] = None,
    page: Annotated[int, Query(description="Page number", ge=1)] = 1,
    size: Annotated[
        int, Query(description="Number of elements per page", ge=1, le=100)
    ] = 50,
    sort: Annotated[
        list[str],
        Query(
            description=(
                "You can sort results using this param with the format "
                "`sort=param1:asc&sort=param2:desc`"
            )
        ),
    ] = ["date:desc"],
) -> PageApiEcoindexes:
    ecoindexes = await get_ecoindex_result_list_db(
        date_from=date_from,
        date_to=date_to,
        host=host,
        version=version,
        page=page,
        size=size,
        sort_params=await get_sort_parameters(
            query_params=sort, model=ApiEcoindex
        ),  # type: ignore
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
    id: UUID = Path(
        default=..., description="Unique identifier of the ecoindex analysis"
    ),
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
    id: UUID = Path(
        default=..., description="Unique identifier of the ecoindex analysis"
    ),
):
    return FileResponse(
        path=f"{getcwd()}/screenshots/{version.value}/{id}.webp",
        filename=f"{id}.webp",
        content_disposition_type="inline",
        media_type="image/webp",
    )
