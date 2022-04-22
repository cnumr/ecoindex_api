from db.engine import create_db_and_tables, is_database_online
from fastapi.applications import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_health import health
from selenium.common.exceptions import WebDriverException
from settings import (
    CORS_ALLOWED_CREDENTIALS,
    CORS_ALLOWED_HEADERS,
    CORS_ALLOWED_METHODS,
    CORS_ALLOWED_ORIGINS,
)
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from api.ecoindex.routers import ecoindex
from api.helper import format_exception_response
from api.host.routers import host
from api.models.responses import ApiHealth

app = FastAPI(
    title="Ecoindex API",
    version="1.0.0",
    description="Ecoindex API enables you to perform ecoindex analysis of given web pages",
)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=CORS_ALLOWED_CREDENTIALS,
    allow_headers=CORS_ALLOWED_HEADERS,
    allow_methods=CORS_ALLOWED_METHODS,
    allow_origins=CORS_ALLOWED_ORIGINS,
)

app.include_router(router=ecoindex.router)
app.include_router(router=host.router)


@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()


@app.exception_handler(WebDriverException)
async def handle_webdriver_exception(_: Request, exc: WebDriverException):
    if "ERR_NAME_NOT_RESOLVED" in exc.msg:
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content={
                "detail": "This host is unreachable. Are you really sure of this url? 🤔"
            },
        )

    if "ERR_CONNECTION_TIMED_OUT" in exc.msg:
        return JSONResponse(
            status_code=status.HTTP_504_GATEWAY_TIMEOUT,
            content={
                "detail": "Timeout reached when requesting this url. This is probably a temporary issue. 😥"
            },
        )

    exception_response = format_exception_response(exception=exc)
    return JSONResponse(
        content={"detail": exception_response.dict()},
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    )


@app.exception_handler(Exception)
async def validation_exception_handler(_: Request, exc: Exception):
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
