from datetime import date
from typing import List, Optional
from uuid import UUID, uuid1

from api.ecoindex.models.responses import ApiEcoindex
from api.models.enums import Version
from sqlalchemy import func
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.expression import asc
from sqlmodel import select

from db.helper import date_filter
from ecoindex.models import Result


async def save_ecoindex_result_db(
    session: AsyncSession,
    ecoindex_result: Result,
    version: Optional[Version] = Version.v1,
) -> ApiEcoindex:
    db_ecoindex = ApiEcoindex(
        id=str(uuid1()),
        date=ecoindex_result.date,
        url=ecoindex_result.url,
        host=ecoindex_result.url.host,
        width=ecoindex_result.width,
        height=ecoindex_result.height,
        size=ecoindex_result.size,
        nodes=ecoindex_result.nodes,
        requests=ecoindex_result.requests,
        grade=ecoindex_result.grade,
        score=ecoindex_result.score,
        ges=ecoindex_result.ges,
        water=ecoindex_result.water,
        page_type=ecoindex_result.page_type,
        version=version.get_version_number(),
    )
    session.add(db_ecoindex)
    await session.commit()
    await session.refresh(db_ecoindex)

    return db_ecoindex


async def get_count_analysis_db(
    session: AsyncSession, version: Optional[Version] = Version.v1
) -> int:
    result = await session.execute(
        f"SELECT count(*) FROM apiecoindex WHERE version = {version.get_version_number()}"
    )

    return result.scalar()


async def get_ecoindex_result_list_db(
    session: AsyncSession,
    version: Optional[Version] = Version.v1,
    host: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
    page: int = 1,
    size: int = 50,
) -> List[ApiEcoindex]:
    statement = (
        select(ApiEcoindex)
        .where(ApiEcoindex.version == version.get_version_number())
        .offset((page - 1) * size)
        .limit(size)
    )

    if host:
        statement = statement.where(ApiEcoindex.host == host)
    statement = date_filter(statement=statement, date_from=date_from, date_to=date_to)

    ecoindexes = await session.execute(statement.order_by(asc("date")))

    return ecoindexes.scalars().all()


async def get_ecoindex_result_by_id_db(
    session: AsyncSession, id: UUID, version: Optional[Version] = Version.v1
) -> ApiEcoindex:
    statement = (
        select(ApiEcoindex)
        .where(ApiEcoindex.id == id)
        .where(ApiEcoindex.version == version.get_version_number())
    )
    ecoindex = await session.execute(statement)

    return ecoindex.scalar_one_or_none()


async def get_count_daily_request_per_host(session: AsyncSession, host: str) -> int:
    statement = select(ApiEcoindex).where(
        func.date(ApiEcoindex.date) == date.today(), ApiEcoindex.host == host
    )
    results = await session.execute(statement)
    return len(results.all())
