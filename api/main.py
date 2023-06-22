from fastapi.applications import FastAPI

from api.domain.ecoindex import routes as ecoindex_routes
from api.domain.host import routes as host_routes
from api.domain.task import routes as task_routes
from db.engine import create_db_and_tables

app = FastAPI(
    title="Ecoindex API",
    version="1.0.0",
    description=(
        "Ecoindex API enables you to perform ecoindex analysis of given web pages"
    ),
)

app.include_router(router=ecoindex_routes.router)
app.include_router(router=host_routes.router)
app.include_router(router=task_routes.router)

from api.application.exception_handler import handle_exceptions
from api.application.middleware.cors import add_cors_middleware
from api.domain.health.routes import add_healthcheck_route

add_healthcheck_route()
add_cors_middleware()
handle_exceptions()


@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()
