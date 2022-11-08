from api.main import app
from fastapi.middleware.cors import CORSMiddleware
from settings import (
    CORS_ALLOWED_CREDENTIALS,
    CORS_ALLOWED_HEADERS,
    CORS_ALLOWED_METHODS,
    CORS_ALLOWED_ORIGINS,
)


async def add_cors_middleware():
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=CORS_ALLOWED_CREDENTIALS,
        allow_headers=CORS_ALLOWED_HEADERS,
        allow_methods=CORS_ALLOWED_METHODS,
        allow_origins=CORS_ALLOWED_ORIGINS,
    )
