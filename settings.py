from environ import Env

env = Env()
env.read_env()

CORS_ALLOWED_CREDENTIALS = env.bool("CORS_ALLOWED_CREDENTIALS", default=True)
CORS_ALLOWED_HEADERS = env("CORS_ALLOWED_HEADERS", cast=list, default=["*"])
CORS_ALLOWED_METHODS = env("CORS_ALLOWED_METHODS", cast=list, default=["*"])
CORS_ALLOWED_ORIGINS = env("CORS_ALLOWED_ORIGINS", cast=list, default=["*"])
DAILY_LIMIT_PER_HOST = env("DAILY_LIMIT_PER_HOST", cast=int, default=0)
WAIT_BEFORE_SCROLL = env("WAIT_BEFORE_SCROLL", cast=int, default=3)
WAIT_AFTER_SCROLL = env("WAIT_AFTER_SCROLL", cast=int, default=3)
DATABASE_URL = env("DATABASE_URL", cast=str, default="sqlite+aiosqlite:///./sql_app.db")
