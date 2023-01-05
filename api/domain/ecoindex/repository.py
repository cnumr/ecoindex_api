from datetime import date
from typing import List
from uuid import UUID

from ecoindex.models import Result
from sqlalchemy import func
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.sql.expression import asc, desc
from sqlmodel import select

from api.domain.ecoindex.models.responses import ApiEcoindex
from api.models.enums import Version
from api.models.sort import Sort
from db.engine import engine
from db.helper import date_filter


async def get_count_analysis_db(
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

    async with AsyncSession(engine) as session:
        result = await session.execute(statement=statement)

        return result.scalar()


async def get_rank_analysis_db(
    ecoindex: Result, version: Version | None = Version.v1
) -> int | None:
    async with AsyncSession(engine) as session:
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
    version: Version | None = Version.v1,
    host: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    page: int | None = 1,
    size: int | None = 50,
    sort_params: List[Sort] = [],
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

    for sort in sort_params:
        if sort.sort == "asc":
            sort_parameter = asc(sort.clause)
        elif sort.sort == "desc":
            sort_parameter = desc(sort.clause)

        statement = statement.order_by(sort_parameter)

    async with AsyncSession(engine) as session:
        ecoindexes = await session.execute(statement)

        return ecoindexes.scalars().all()


async def get_ecoindex_result_by_id_db(
    id: UUID, version: Version | None = Version.v1
) -> ApiEcoindex:
    statement = (
        select(ApiEcoindex)
        .where(ApiEcoindex.id == id)
        .where(ApiEcoindex.version == version.get_version_number())
    )

    async with AsyncSession(engine) as session:
        ecoindex = await session.execute(statement)

        return ecoindex.scalar_one_or_none()


async def get_count_daily_request_per_host(host: str) -> int:
    statement = select(ApiEcoindex).where(
        func.date(ApiEcoindex.date) == date.today(), ApiEcoindex.host == host
    )

    async with AsyncSession(engine) as session:
        results = await session.execute(statement)

        return len(results.all())


async def get_latest_result(host: str) -> ApiEcoindex:
    statement = (
        select(ApiEcoindex)
        .where(ApiEcoindex.host == host)
        .order_by(desc(ApiEcoindex.date))
        .limit(1)
    )

    async with AsyncSession(engine) as session:
        result = await session.execute(statement)

        return result.scalar_one_or_none()
