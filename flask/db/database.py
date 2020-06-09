import psycopg2
import pybreaker

from core.config import DATABASE_URL, MAX_CONNECTIONS_COUNT, MIN_CONNECTIONS_COUNT
from core.log import logger

db_breaker = pybreaker.CircuitBreaker(fail_max=5, reset_timeout=60)


class DataBase:
    def __init__(self):

        logger.info("Database Init")
        self.connect_to_db()

    @db_breaker
    def connect_to_db(self):

        self.pool_min_connections = MIN_CONNECTIONS_COUNT
        self.pool_max_connections = MAX_CONNECTIONS_COUNT

        logger.info("Attempting DB connection")

        self.db_conn = psycopg2.connect(DATABASE_URL)
        self.db_conn.autocommit = True

        logger.debug("DB Conn Params", conn=self.db_conn.dsn)
        logger.info("DB connected")
