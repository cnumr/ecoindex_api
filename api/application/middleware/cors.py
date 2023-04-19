from fastapi.middleware.cors import CORSMiddleware

from api.main import app
from settings import Settings


def add_cors_middleware():
    app.add_middleware(
        CORSMiddleware,
        allow_credentials=Settings().CORS_ALLOWED_CREDENTIALS,
        allow_headers=Settings().CORS_ALLOWED_HEADERS,
        allow_methods=Settings().CORS_ALLOWED_METHODS,
        allow_origins=Settings().CORS_ALLOWED_ORIGINS,
    )
