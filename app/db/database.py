import psycopg2

from app.core.log import logger
from app.core.config import DATABASE_URL, MAX_CONNECTIONS_COUNT, MIN_CONNECTIONS_COUNT


class DataBase:
    def __init__(self):

        logger.info("Database Connecting")

        self._connect_to_db()

    def connect(self):

        self.pool_min_connections = MIN_CONNECTIONS_COUNT
        self.pool_max_connections = MAX_CONNECTIONS_COUNT

        self.db_conn = psycopg2.connect(DATABASE_URL)
        self.db_conn.autocommit = True

        logger.info("DB connected")

        return self.db_conn
