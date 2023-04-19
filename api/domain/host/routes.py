from datetime import date

from fastapi import Path, status
from fastapi.param_functions import Query
from fastapi.responses import Response
from fastapi.routing import APIRouter

from api.domain.host.models.host import Host, PageHosts
from api.domain.host.repository import get_count_hosts_db, get_host_list_db
from api.domain.task.models.examples import example_daily_limit_response
from api.helper import get_status_code
from api.models.enums import Version
from common.helper import check_quota

router = APIRouter()


@router.get(
    name="Get host list",
    path="/{version}/hosts",
    response_model=PageHosts,
    response_description="List ecoindex hosts",
    responses={
        status.HTTP_206_PARTIAL_CONTENT: {"model": PageHosts},
        status.HTTP_404_NOT_FOUND: {"model": PageHosts},
    },
    tags=["Host"],
    description=(
        "This returns a list of hosts that "
        "ran an ecoindex analysis order by most request made"
    ),
)
async def get_host_list(
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
    q: str = Query(default=None, description="Filter by partial host name"),
    page: int | None = Query(1, description="Page number", ge=1),
    size: int
    | None = Query(50, description="Number of elements per page", ge=1, le=100),
) -> PageHosts:
    hosts = await get_host_list_db(
        date_from=date_from,
        date_to=date_to,
        q=q,
        version=version,
        page=page,
        size=size,
    )

    total_hosts = await get_count_hosts_db(
        version=version, q=q, date_from=date_from, date_to=date_to
    )

    response.status_code = await get_status_code(items=hosts, total=total_hosts)

    return PageHosts(items=hosts, total=total_hosts, page=page, size=size)


@router.get(
    name="Get host details",
    path="/{version}/hosts/{host}",
    response_description="Host details",
    responses={
        status.HTTP_200_OK: {"model": Host},
        status.HTTP_404_NOT_FOUND: {"model": Host},
        status.HTTP_429_TOO_MANY_REQUESTS: example_daily_limit_response,
    },
    tags=["Host"],
    description=(
        "This returns the details of a host. If no no quota is set, "
        "remaining_daily_requests will be null"
    ),
)
async def get_daily_remaining(
    version: Version = Path(
        default=...,
        title="Engine version",
        description="Engine version used to run the analysis (v0 or v1)",
        example=Version.v1.value,
    ),
    host: str = Path(
        default=...,
        title="Host name",
        description="Host name used to run the analysis",
        example="www.ecoindex.fr",
    ),
) -> Host:
    return Host(
        name=host,
        remaining_daily_requests=await check_quota(host=host),
        total_count=await get_count_hosts_db(
            name=host, version=version, group_by_host=False
        ),
    )
