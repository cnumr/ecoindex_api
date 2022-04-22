from api.models.enums import Version
from api.models.examples import example_exception_response
from api.statistic.db.statistic import get_statistics_db
from api.statistic.models.responses import ApiStatistic
from db.engine import get_session
from fastapi import APIRouter, Depends, Path
from sqlmodel.ext.asyncio.session import AsyncSession

router = APIRouter()


@router.get(
    path="/{version}/statistics",
    response_model=ApiStatistic,
    tags=["Statistic"],
    responses={500: example_exception_response},
    description="Get statistics of the ecoindex analysis",
)
async def get_statistics(
    session: AsyncSession = Depends(get_session),
    version: Version = Path(
        default=..., title="Engine version used to run the analysis"
    ),
):
    return await get_statistics_db(session=session, version=version)
