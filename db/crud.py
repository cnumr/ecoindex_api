from datetime import date
from typing import List, Optional

from api.models import ApiResult
from ecoindex.models import Result
from sqlalchemy import asc, func
from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import and_

from db.models import Ecoindex


def save_ecoindex_result_db(db: Session, ecoindex_result: Result) -> ApiResult:
    db_ecoindex = Ecoindex(
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
    )
    db.add(db_ecoindex)
    db.commit()
    db.refresh(db_ecoindex)

    return db_ecoindex


def get_ecoindex_result_list_db(
    db: Session, host: Optional[str] = None
) -> List[ApiResult]:
    return db.query(Ecoindex).order_by(asc("date")).all()


def get_count_daily_request_per_host(db: Session, host: str) -> int:
    return (
        db.query(Ecoindex)
        .filter(and_(func.date(Ecoindex.date) == date.today(), Ecoindex.host == host))
        .count()
    )
