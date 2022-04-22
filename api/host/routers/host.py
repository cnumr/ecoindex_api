from datetime import date
from typing import Optional

from api.helper import get_status_code
from api.host.db.host import get_count_hosts_db, get_host_list_db
from api.host.models.host import PageHosts
from api.models.enums import Version
from api.models.examples import example_exception_response
from db.engine import get_session
from fastapi import Path, status
from fastapi.param_functions import Query
from fastapi.params import Depends
from fastapi.responses import Response
from fastapi.routing import APIRouter
from sqlmodel.ext.asyncio.session import AsyncSession

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
    session: AsyncSession = Depends(get_session),
    version: Version = Path(
        default=..., title="Engine version used to run the analysis"
    ),
    date_from: Optional[date] = Query(
        None, description="Start date of the filter elements (example: 2020-01-01)"
    ),
    date_to: Optional[date] = Query(
        None, description="End date of the filter elements  (example: 2020-01-01)"
    ),
    q: str = Query(default=None, description="Filter by partial host name"),
    page: Optional[int] = Query(1, description="Page number", gte=1),
    size: Optional[int] = Query(
        50, description="Number of elements per page", gte=1, lte=100
    ),
) -> PageHosts:
    hosts = await get_host_list_db(
        session=session,
        date_from=date_from,
        date_to=date_to,
        q=q,
        version=version,
        page=page,
        size=size,
    )

    total_hosts = await get_count_hosts_db(
        session=session, version=version, q=q, date_from=date_from, date_to=date_to
    )

    response.status_code = get_status_code(items=hosts, total=total_hosts)

    return PageHosts(items=hosts, total=total_hosts, page=page, size=size)
