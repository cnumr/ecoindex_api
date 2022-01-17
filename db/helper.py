from datetime import date
from typing import Optional

from api.ecoindex.models.responses import ApiEcoindex
from sqlmodel.sql.expression import SelectOfScalar


def date_filter(
    statement: SelectOfScalar,
    date_from: Optional[date] = None,
    date_to: Optional[date] = None,
) -> SelectOfScalar:
    if date_from:
        statement = statement.where(ApiEcoindex.date >= date_from)

    if date_to:
        statement = statement.where(ApiEcoindex.date <= date_to)

    return statement
