from datetime import date
from typing import List, Optional

from api.host.db.host import get_host_list_db
from api.models.enums import Version
from api.models.examples import example_exception_response
from db.engine import get_session
from fastapi import Path
from fastapi.param_functions import Query
from fastapi.params import Depends
from fastapi.routing import APIRouter
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()


@router.get(
    path="/{version}/hosts",
    response_model=List[str],
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
) -> List[str]:
    hosts = await get_host_list_db(
        session=session, date_from=date_from, date_to=date_to, q=q, version=version
    )
    return hosts
