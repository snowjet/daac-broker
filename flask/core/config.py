import os
import pathlib

from dotenv import load_dotenv
from starlette.datastructures import CommaSeparatedStrings

API_V1_STR = "/api"

JWT_TOKEN_PREFIX = "Token"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # one week

env_file = os.environ.get("env_file", ".env")
load_dotenv(env_file)

LOG_LEVEL = os.environ.get("LOG_LEVEL", "INFO").upper()
PROJECT_NAME = os.getenv("PROJECT_NAME", "app")
DATABASE_URL = os.getenv("DATABASE_URL", "")

GUACADMIN_PASSWORD = os.getenv("GUACADMIN_PASSWORD", "guacadmin")

GUAC_URL = os.getenv("GUAC_URL", "https://guac.apps-crc.testing")

if not DATABASE_URL:
    POSTGRES_HOST = os.getenv("POSTGRES_SERVICE_HOST", "postgres")
    POSTGRES_PORT = int(os.getenv("POSTGRES_SERVICE_PORT", 5432))
    POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASS = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_NAME = os.getenv("POSTGRES_DB", "guacamole_db")

    DATABASE_URL = f"host='{POSTGRES_HOST}' port='{POSTGRES_PORT}' dbname='{POSTGRES_NAME}' user='{POSTGRES_USER}' password='{POSTGRES_PASS}'"

# Placeholder for connection pooling
MAX_CONNECTIONS_COUNT = int(os.getenv("MAX_CONNECTIONS_COUNT", 10))
MIN_CONNECTIONS_COUNT = int(os.getenv("MIN_CONNECTIONS_COUNT", 10))

ALLOWED_HOSTS = CommaSeparatedStrings(os.getenv("ALLOWED_HOSTS", ""))
SECRET_KEY = os.getenv("SECRET_KEY", "85aa579473e7692bf224c12ad8824b766eb9894890333a77")

# Set or retrieve OpenShift Namespace for
namespace_filepath = "/run/secrets/kubernetes.io/serviceaccount/namespace"
ns_path = pathlib.Path(namespace_filepath)
if ns_path.is_file():
    file_namespace = open("/run/secrets/kubernetes.io/serviceaccount/namespace", "r")
    NAMESPACE = file_namespace.read()
else:
    NAMESPACE = os.getenv("NAMESPACE", "default")

sso_config = {}
sso_config["PUBLIC_KEY"] = os.getenv("PUBLIC_KEY", "RSA Public Key")
