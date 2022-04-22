from typing import Optional

from api.ecoindex.models.responses import ApiEcoindex
from api.models.enums import Version
from api.statistic.models.responses import ApiStatistic
from sqlalchemy import func
from sqlmodel.ext.asyncio.session import AsyncSession


async def get_min(
    session: AsyncSession,
    field: str,
    version: Optional[Version] = Version.v1,
) -> ApiStatistic:
    qry = session.query(
        func.max(ApiEcoindex.size).label("max_score"),
        func.min(ApiEcoindex.size).label("min_score"),
        func.median(ApiEcoindex.size).label("median_score"),
    )
    res = qry.one()
    return res
