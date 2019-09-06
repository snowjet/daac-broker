import psycopg2

from core.config import DATABASE_URL, MAX_CONNECTIONS_COUNT, MIN_CONNECTIONS_COUNT
from core.log import logger


class DataBase:
    def __init__(self):

        logger.info("Database Init")
        self.connect_to_db()

    def connect_to_db(self):

        self.pool_min_connections = MIN_CONNECTIONS_COUNT
        self.pool_max_connections = MAX_CONNECTIONS_COUNT

        logger.info("Attempting DB connection")

        self.db_conn = psycopg2.connect(DATABASE_URL)
        self.db_conn.autocommit = True

        logger.debug("DB Conn Params", conn=self.db_conn.dsn)
        logger.info("DB connected")
