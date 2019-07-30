import os

from dotenv import load_dotenv
from starlette.datastructures import CommaSeparatedStrings, Secret

API_V1_STR = "/api"

JWT_TOKEN_PREFIX = "Token"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # one week

load_dotenv(".env")

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()

DATABASE_URL = os.getenv("DATABASE_URL", "")

if not DATABASE_URL:
    POSTGRES_HOST = os.getenv("POSTGRES_HOST", "postgres")
    POSTGRES_PORT = int(os.getenv("POSTGRES_PORT", 5432))
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_NAME = os.getenv("POSTGRES_DB", "guacamole_db")

    DATABASE_URL = f"host={POSTGRES_HOST} port={POSTGRES_PORT} dbname={POSTGRES_NAME} user={POSTGRES_USER} password={POSTGRES_PASS}"

# Placeholder for connection pooling
MAX_CONNECTIONS_COUNT = int(os.getenv("MAX_CONNECTIONS_COUNT", 10))
MIN_CONNECTIONS_COUNT = int(os.getenv("MIN_CONNECTIONS_COUNT", 10))

ALLOWED_HOSTS = CommaSeparatedStrings(os.getenv("ALLOWED_HOSTS", ""))
SECRET_KEY = Secret(os.getenv("SECRET_KEY", "secret key for project"))
