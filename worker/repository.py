from uuid import UUID

from ecoindex.models import Result
from sqlalchemy.ext.asyncio.session import AsyncSession

from api.domain.ecoindex.models.responses import ApiEcoindex
from api.domain.ecoindex.repository import get_count_analysis_db, get_rank_analysis_db
from api.models.enums import Version
from db.engine import engine


async def save_ecoindex_result_db(
    id: UUID,
    ecoindex_result: Result,
    version: Version | None = Version.v1,
) -> ApiEcoindex:
    ranking = await get_rank_analysis_db(ecoindex=ecoindex_result, version=version)
    total_results = await get_count_analysis_db(version=version)

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

    async with AsyncSession(engine) as session:
        session.add(db_ecoindex)
        await session.commit()
        await session.refresh(db_ecoindex)

        return db_ecoindex
