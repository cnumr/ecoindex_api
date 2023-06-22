from pydantic import BaseSettings


class Settings(BaseSettings):
    CHROME_VERSION_MAIN: int | None = None
    CORS_ALLOWED_CREDENTIALS: bool = True
    CORS_ALLOWED_HEADERS: list = ["*"]
    CORS_ALLOWED_METHODS: list = ["*"]
    CORS_ALLOWED_ORIGINS: list = ["*"]
    DAILY_LIMIT_PER_HOST: int = 0
    DATABASE_URL: str = "sqlite+aiosqlite:///./sql_app.db"
    ENABLE_SCREENSHOT: bool = False
    SCREENSHOTS_GID: int | None = None
    SCREENSHOTS_UID: int | None = None
    WAIT_BEFORE_SCROLL: int = 3
    WAIT_AFTER_SCROLL: int = 3
    WORKER_BROKER_URL: str = "redis://localhost:6379/0"
    WORKER_BACKEND_URL: str = "redis://localhost:6379/0"

    class Config:
        env_file = ".env"
