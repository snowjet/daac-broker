import os
import psycopg2

from app.core.log import logger
from app.core.config import DATABASE_URL, MAX_CONNECTIONS_COUNT, MIN_CONNECTIONS_COUNT


class DataBase:
    def __init__(self):

        logger.info("Database Connecting")

        self._connect_to_db()

    def _connect_to_db(self):

        self.pool_min_connections = MIN_CONNECTIONS_COUNT
        self.pool_max_connections = MAX_CONNECTIONS_COUNT

        self.db_conn = psycopg2.connect(DATABASE_URL)
        self.db_conn.autocommit = True

        logger.info("DB connected")

    def confirm_db_connection(self):

        # Read-only integer attribute: 0 if the connection is open, nonzero if it is closed or broken.
        conn_status = self.db_conn.closed
        logger.debug("DB connection status", connection_status=conn_status)

        if conn_status:
            logger.info("DB is not connected - reconnecting")
            self._connect_to_db()

    def disconnect(self):

        logger.info("Closing DB connection")

        self.db_conn.close()

        logger.info("Closed DB connection")

    def test(self):

        return "Test"

    def load_schmea_safe(self):

        self.db_conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = self.db_conn.cursor()

        # First check if postgres already has a schema
        cursor.execute(
            "SELECT EXISTS ( SELECT 1 \
                        FROM   pg_tables \
                        WHERE  schemaname = 'public' \
                        AND    tablename = 'guacamole_connection' \
                        );"
        )

        table_exists = cursor.fetchall()

        if not table_exists[0][0]:
            return_msg = "Schema Not Found - Adding schema"
            logger.info(return_msg)
            db_schema = os.path.join(os.path.dirname(__file__), "db_schema/initdb.sql")
            sql_file = open(db_schema, "r")
            cursor.execute(sql_file.read())
        else:
            return_msg = "tables already has a schema"
            logger.info(return_msg)

        return return_msg
