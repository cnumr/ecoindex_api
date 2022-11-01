from datetime import date
from typing import List

from api.domain.ecoindex.models.responses import ApiEcoindex
from api.models.enums import Version
from db.helper import date_filter
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlmodel import select


async def get_host_list_db(
    session: AsyncSession,
    version: Version | None = Version.v1,
    q: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
    page: int | None = 1,
    size: int | None = 50,
) -> List[str]:
    statement = (
        select(ApiEcoindex.host)
        .where(ApiEcoindex.version == version.get_version_number())
        .offset(size * (page - 1))
        .limit(size)
    )

    if q:
        statement = statement.filter(ApiEcoindex.host.like(f"%{q}%"))

    statement = date_filter(statement=statement, date_from=date_from, date_to=date_to)

    statement = statement.group_by(ApiEcoindex.host).order_by(ApiEcoindex.host)

    hosts = await session.execute(statement)

    return hosts.scalars().all()


async def get_count_hosts_db(
    session: AsyncSession,
    version: Version | None = Version.v1,
    q: str | None = None,
    date_from: date | None = None,
    date_to: date | None = None,
) -> int:
    sub_statement = (
        f"SELECT host FROM apiecoindex WHERE version = {version.get_version_number()}"
    )
    if q:
        sub_statement += f" AND host LIKE '%{q}%'"

    if date_from:
        sub_statement += f" AND date >= '{date_from}'"

    if date_to:
        sub_statement += f" AND date <= '{date_to}'"

    sub_statement += " GROUP BY host"

    statement = f"SELECT count(*) FROM ({sub_statement}) t"
    result = await session.execute(statement=statement)

    return result.scalar()
