from db.database import create_db_and_tables, is_database_online
from fastapi.applications import FastAPI
from fastapi_health import health
from fastapi_pagination.api import add_pagination
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from api.helper import format_exception_response
from api.models import ApiHealth
from api.routers import ecoindex, host

app = FastAPI(
    title="Ecoindex API",
    version="1.0.0",
    description="Ecoindex API enables you to perform ecoindex analysis of given web pages",
)

app.include_router(router=ecoindex.router)
app.include_router(router=host.router)


@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()


@app.exception_handler(Exception)
async def validation_exception_handler(request: Request, exc: Exception):
    exception_response = format_exception_response(exception=exc)
    return JSONResponse(
        content={"detail": exception_response.dict()},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


app.add_api_route(
    path="/health",
    endpoint=health([is_database_online]),
    tags=["Infra"],
    name="Get healthcheck",
    description="Check health status of components of the API (database...)",
    response_model=ApiHealth,
)


add_pagination(app)
