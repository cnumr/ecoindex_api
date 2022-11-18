from fastapi_health import health

from api.domain.health.chromedriver import is_chromedriver_healthy
from api.main import app
from api.models.responses import ApiHealth
from db.engine import is_database_online


def add_healthcheck_route():
    app.add_api_route(
        path="/health",
        endpoint=health([is_database_online, is_chromedriver_healthy]),
        tags=["Infra"],
        name="Get healthcheck",
        description="Check health status of components of the API (database...)",
        response_model=ApiHealth,
    )
