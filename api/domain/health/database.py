from fastapi.param_functions import Depends

from db.engine import get_session


def is_database_online(session: bool = Depends(get_session)):
    return {"database": bool(session)}
