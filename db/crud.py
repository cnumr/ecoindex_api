from datetime import date
from typing import List, Optional
from uuid import uuid4

from api.models import ApiEcoindex
from ecoindex.models import Result
from sqlalchemy import func
from sqlalchemy.sql.expression import asc
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from db.database import engine


async def save_ecoindex_result_db(ecoindex_result: Result, version: int) -> ApiEcoindex:
    db_ecoindex = ApiEcoindex(
        id=str(uuid4()),
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
        version=version,
    )
    with AsyncSession(engine) as session:
        session.add(db_ecoindex)
        session.commit()

    return db_ecoindex


async def get_ecoindex_result_list_db(
    version: int,
    host: Optional[str] = None,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> List[ApiEcoindex]:
    async with AsyncSession(engine) as session:
        statement = select(ApiEcoindex).where(ApiEcoindex.version == version)

        if host:
            statement = statement.where(ApiEcoindex.host == host)

        if date_from:
            statement = statement.where(ApiEcoindex.date >= date_from)

        if date_to:
            statement = statement.where(ApiEcoindex.date <= date_to)

        ecoindexes = await session.exec(statement.order_by(asc("date")))

        return ecoindexes.all()


async def get_count_daily_request_per_host(host: str) -> int:
    statement = select(ApiEcoindex).where(
        func.date(ApiEcoindex.date) == date.today(), ApiEcoindex.host == host
    )
    with AsyncSession(engine) as session:
        results = await session.exec(statement)
        return len(results.all())
