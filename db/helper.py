from datetime import date

from sqlmodel.sql.expression import SelectOfScalar

from api.domain.ecoindex.models.responses import ApiEcoindex

SelectOfScalar.inherit_cache = True  # type: ignore


def date_filter(
    statement: SelectOfScalar,
    date_from: date | None = None,
    date_to: date | None = None,
) -> SelectOfScalar:
    if date_from:
        statement = statement.where(ApiEcoindex.date >= date_from)

    if date_to:
        statement = statement.where(ApiEcoindex.date <= date_to)

    return statement
