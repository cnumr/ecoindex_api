from datetime import date
from typing import List, Optional

from db.crud import get_host_list_db
from db.database import get_session
from fastapi.param_functions import Query
from fastapi.params import Depends
from fastapi.routing import APIRouter
from fastapi_pagination import Page, paginate
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()


@router.get(
    path="/v1/hosts",
    response_model=Page[str],
    response_description="List ecoindex hosts",
    tags=["Host"],
    description="This returns a list of hosts that ran an ecoindex analysis order by most request made",
)
async def get_host_list(
    session: AsyncSession = Depends(get_session),
    date_from: Optional[date] = Query(
        None, description="Start date of the filter elements (example: 2020-01-01)"
    ),
    date_to: Optional[date] = Query(
        None, description="End date of the filter elements  (example: 2020-01-01)"
    ),
    q: str = Query(default=None, description="Filter by partial host name"),
) -> Page[str]:
    hosts = await get_host_list_db(
        session=session, date_from=date_from, date_to=date_to, q=q
    )
    return paginate(hosts)
