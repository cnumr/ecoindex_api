from db.database import create_db_and_tables, is_database_online
from fastapi.applications import FastAPI
from fastapi_health import health
from fastapi_pagination.api import add_pagination

from api.routers import ecoindex

app = FastAPI(
    title="Ecoindex API",
    version="1.0.0",
    description="Ecoindex API enables you to perform ecoindex analysis of given web pages",
)

app.include_router(ecoindex.router)


@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()


app.add_api_route("/health", health([is_database_online]))
add_pagination(app)
