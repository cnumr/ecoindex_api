from fastapi_health import health

from api.domain.health.database import is_database_online
from api.domain.health.worker import is_worker_healthy
from api.main import app
from api.models.responses import ApiHealth


def add_healthcheck_route():
    app.add_api_route(
        path="/health",
        endpoint=health([is_database_online, is_worker_healthy]),
        tags=["Infra"],
        name="Get healthcheck",
        description="Check health status of components of the API (database...)",
        response_model=ApiHealth,
    )
