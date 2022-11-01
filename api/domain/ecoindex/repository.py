from datetime import date
from typing import List
from uuid import UUID

from api.domain.ecoindex.models.responses import ApiEcoindex
from api.models.enums import Version
from db.helper import date_filter
from ecoindex_scraper.models import Result
from sqlalchemy import func
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.expression import asc
from sqlmodel import select


async def save_ecoindex_result_db(
    session: AsyncSession,
    id: UUID,
    ecoindex_result: Result,
    version: Version | None = Version.v1,
) -> ApiEcoindex:
    ranking = await get_rank_analysis_db(
        ecoindex=ecoindex_result, session=session, version=version
    )
    total_results = await get_count_analysis_db(session=session, version=version)
    db_ecoindex = ApiEcoindex(
        id=id,
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
        initial_ranking=ranking if ranking else total_results + 1,
        initial_total_results=total_results + 1,
        ecoindex_version=ecoindex_result.ecoindex_version,
    )
    session.add(db_ecoindex)
    await session.commit()
    await session.refresh(db_ecoindex)

    return db_ecoindex


async def get_count_analysis_db(
    session: AsyncSession,
    version: Version | None = Version.v1,
    host: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> int:
    statement = f"SELECT count(*) FROM apiecoindex WHERE version = {version.get_version_number()}"

    if host:
        statement += f" AND host = '{host}'"

    if date_from:
        statement += f" AND date >= '{date_from}'"

    if date_to:
        statement += f" AND date <= '{date_to}'"

    result = await session.execute(statement=statement)

    return result.scalar()


async def get_rank_analysis_db(
    ecoindex: Result, session: AsyncSession, version: Version | None = Version.v1
) -> int | None:
    result = await session.execute(
        (
            "SELECT ranking FROM ("
            "SELECT *, ROW_NUMBER() OVER (ORDER BY score DESC) ranking "
            "FROM apiecoindex "
            f"WHERE version={version.get_version_number()} "
            "ORDER BY score DESC) t "
            f"WHERE score <= {ecoindex.score} "
            "LIMIT 1;"
        )
    )

    return result.scalar()


async def get_ecoindex_result_list_db(
    session: AsyncSession,
    version: Version | None = Version.v1,
    host: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    page: int | None = 1,
    size: int | None = 50,
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
    session: AsyncSession, id: UUID, version: Version | None = Version.v1
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
