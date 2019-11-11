import os

import psycopg2

from core.log import logger
from db.database import DataBase

from crud.user import update_users_db_password
from core.config import GUACADMIN_PASSWORD

logger.info("Get DB instance")
db = DataBase()


def get_database_connection():
    # Read-only integer attribute:
    # 0 if the connection is open
    # nonzero if it is closed or broken
    conn_status = db.db_conn.closed
    logger.debug("DB connection status", connection_status=conn_status)

    if conn_status:
        logger.info("DB is not connected - reconnecting")
        db.connect_to_db()

    return db.db_conn


def disconnect_from_database():
    logger.info("Closing DB connection")
    db.db_conn.close()
    logger.info("Closed DB connection")


def test():
    return "Test"


def load_schema_safe():

    db_conn = get_database_connection()
    db_conn.set_isolation_level(psycopg2.extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = db_conn.cursor()

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
        update_users_db_password(GUACADMIN_PASSWORD)
    else:
        return_msg = "tables already has a schema"
        logger.info(return_msg)

    cursor.close()

    return return_msg
