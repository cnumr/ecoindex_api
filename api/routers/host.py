from typing import List

from api.models import ApiHost
from db.crud import get_host_list_db
from db.database import get_session
from fastapi.param_functions import Query
from fastapi.params import Depends
from fastapi.routing import APIRouter, APIWebSocketRoute
from fastapi_pagination import Page, paginate
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()


@router.get(
    path="/v1/hosts",
    response_model=List[ApiHost],
    response_description="List ecoindex hosts",
    tags=["Host"],
    description="This returns a list of hosts that ran an ecoindex analysis order by most request made",
)
async def get_host_list(
    session: AsyncSession = Depends(get_session),
    q: str = Query(None, description="Filter by partial host name"),
) -> Page[ApiHost]:
    hosts: List[ApiHost] = await get_host_list_db(session=session, q=q)
    return paginate(hosts)
