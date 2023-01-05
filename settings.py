from email.policy import default

from environ import Env

env = Env()
env.read_env()

CHROME_VERSION_MAIN = env("CHROME_VERSION_MAIN", cast=int, default=None)
CORS_ALLOWED_CREDENTIALS = env.bool("CORS_ALLOWED_CREDENTIALS", default=True)
CORS_ALLOWED_HEADERS = env("CORS_ALLOWED_HEADERS", cast=list, default=["*"])
CORS_ALLOWED_METHODS = env("CORS_ALLOWED_METHODS", cast=list, default=["*"])
CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS", cast=list, default=["*"])
DAILY_LIMIT_PER_HOST = env("DAILY_LIMIT_PER_HOST", cast=int, default=0)
DATABASE_URL = env("DATABASE_URL", cast=str, default="sqlite+aiosqlite:///./sql_app.db")
ENABLE_SCREENSHOT = env("ENABLE_SCREENSHOT", cast=bool, default=False)
MERCURE_URL = env(
    "MERCURE_URL", cast=str, default="https://mercure/.well-known/mercure"
)
MERCURE_PUBLISHER_JWT_KEY = env("MERCURE_PUBLISHER_JWT_KEY", cast=str, default=None)
MERCURE_SUBSCRIBER_JWT_KEY = env("MERCURE_SUBSCRIBER_JWT_KEY", cast=str, default=None)
MERCURE_TOPIC = env("MERCURE_TOPIC", cast=str, default="ecoindex-tasks")
SCREENSHOTS_GID = env("SCREENSHOTS_GID", cast=int, default=None)
SCREENSHOTS_UID = env("SCREENSHOTS_UID", cast=int, default=None)
WAIT_BEFORE_SCROLL = env("WAIT_BEFORE_SCROLL", cast=int, default=3)
WAIT_AFTER_SCROLL = env("WAIT_AFTER_SCROLL", cast=int, default=3)
WORKER_BROKER_URL = env(
    "WORKER_BROKER_URL", cast=str, default="redis://localhost:6379/0"
)
WORKER_BACKEND_URL = env(
    "WORKER_BACKEND_URL", cast=str, default="redis://localhost:6379/1"
)
