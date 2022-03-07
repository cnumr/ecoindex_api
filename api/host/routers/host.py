from datetime import date
from typing import Optional

from api.host.db.host import get_host_list_db
from api.models.enums import Version
from api.models.examples import example_exception_response
from db.engine import get_session
from fastapi import Path
from fastapi.param_functions import Query
from fastapi.params import Depends
from fastapi.routing import APIRouter
from fastapi_pagination import Page, paginate
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()


@router.get(
    path="/{version}/hosts",
    response_model=Page[str],
    response_description="List ecoindex hosts",
    responses={500: example_exception_response},
    tags=["Host"],
    description=(
        "This returns a list of hosts that "
        "ran an ecoindex analysis order by most request made"
    ),
)
async def get_host_list(
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
) -> Page[str]:
    hosts = await get_host_list_db(
        session=session,
        date_from=date_from,
        date_to=date_to,
        q=q,
        version=version,
        page=page,
        size=size,
    )
    return paginate(hosts)
