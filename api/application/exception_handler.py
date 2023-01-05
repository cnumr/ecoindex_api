from fastapi import Request, status
from fastapi.responses import JSONResponse
from selenium.common.exceptions import WebDriverException

from api.application.status import (
    HTTP_520_ECOINDEX_TYPE_ERROR,
    HTTP_521_ECOINDEX_CONNECTION_ERROR,
)
from api.main import app
from common.exception import QuotaExceededException
from common.helper import format_exception_response


async def handle_exceptions():
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

        exception_response = await format_exception_response(exception=exc)
        return JSONResponse(
            content={"detail": exception_response.dict()},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    @app.exception_handler(RuntimeError)
    async def handle_screenshot_not_found_exception(_: Request, exc: FileNotFoundError):
        return JSONResponse(
            content={"detail": str(exc)},
            status_code=status.HTTP_404_NOT_FOUND,
        )

    @app.exception_handler(TypeError)
    async def handle_resource_type_error(_: Request, exc: TypeError):
        return JSONResponse(
            content={"detail": exc.args[0]},
            status_code=HTTP_520_ECOINDEX_TYPE_ERROR,
        )

    @app.exception_handler(ConnectionError)
    async def handle_connection_error(_: Request, exc: ConnectionError):
        return JSONResponse(
            content={"detail": exc.args[0]},
            status_code=HTTP_521_ECOINDEX_CONNECTION_ERROR,
        )

    @app.exception_handler(QuotaExceededException)
    async def handle_quota_exceeded_exception(_: Request, exc: QuotaExceededException):
        return JSONResponse(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            content={"detail": exc.__dict__},
        )

    @app.exception_handler(Exception)
    async def handle_exception(_: Request, exc: Exception):
        exception_response = await format_exception_response(exception=exc)
        return JSONResponse(
            content={"detail": exception_response.dict()},
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )
