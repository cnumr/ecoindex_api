from environ import Env

env = Env()
env.read_env()

DAILY_LIMIT_PER_HOST = env("DAILY_LIMIT_PER_HOST", cast=int, default=0)
DATABASE_URL = env("DATABASE_URL", cast=str, default="sqlite:///./sql_app.db")
