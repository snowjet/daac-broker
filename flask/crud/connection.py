from core.log import logger
from crud.user import get_user_entity_id
from db.db_utils import get_database_connection

import psycopg2.extras

db_conn = get_database_connection()


def get_connections(username):
    """Returns a list of connections for a user"""

    cursor = db_conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    cursor.execute(
        "SELECT connection_name FROM guacamole_connection JOIN guacamole_connection_permission \
            ON guacamole_connection.connection_id = guacamole_connection_permission.connection_id \
            JOIN guacamole_entity \
            ON guacamole_connection_permission.entity_id = guacamole_entity.entity_id \
            where guacamole_entity.name = %s;",
        (username,),
    )

    connection_names = []
    results = cursor.fetchall()

    for row in results:
        connection_names.append(dict(row))

    # Close communication with the database
    cursor.close()

    return connection_names


def get_connection_id(hostname):

    cursor = db_conn.cursor()

    cursor.execute(
        "SELECT connection_id from guacamole_connection where connection_name=%s;",
        (hostname,),
    )
    connection_id = cursor.fetchone()

    # Close communication with the database
    cursor.close()

    return connection_id


def create_connection(username, hostname, password, protocol="rdp", port="3389"):
    con_name = hostname
    cursor = db_conn.cursor()

    # hard coding the username of the container for the timebeing
    username = "user"

    # Need to check if the hostname already exists - then we are just updating - Determine the connection_id
    cursor.execute(
        "SELECT connection_id FROM guacamole_connection WHERE connection_name = %s AND parent_id IS NULL;",
        (hostname,),
    )
    connection_id = cursor.fetchone()

    if connection_id is None:
        logger.info("Adding new connection", con_name=con_name)

        cursor.execute(
            "INSERT INTO guacamole_connection (connection_name, protocol) VALUES (%s, %s);",
            (con_name, protocol),
        )

        # Now Determine the connection_id
        cursor.execute(
            "SELECT connection_id FROM guacamole_connection WHERE connection_name = %s AND parent_id IS NULL;",
            (con_name,),
        )
        connection_id = cursor.fetchone()

        # Update entry
        cursor.execute(
            "INSERT INTO guacamole_connection_parameter VALUES (%s, 'hostname', %s);",
            (connection_id[0], hostname),
        )
        cursor.execute(
            "INSERT INTO guacamole_connection_parameter VALUES (%s, 'port', %s);",
            (connection_id[0], port),
        )
        cursor.execute(
            "INSERT INTO guacamole_connection_parameter VALUES (%s, 'username', %s);",
            (connection_id[0], username),
        )
        cursor.execute(
            "INSERT INTO guacamole_connection_parameter VALUES (%s, 'password', %s);",
            (connection_id[0], password),
        )
        cursor.execute(
            "INSERT INTO guacamole_connection_parameter VALUES (%s, 'ignore-cert', %s);",
            (connection_id[0], 'true'),
        )

    else:
        logger.error(
            "Connection ID already exists - use update",
            con_name=con_name,
            conneciton_id=connection_id[0],
        )

    cursor.close()

    return True


def update_connection(username, hostname, password, protocol="rdp", port="3389"):
    con_name = hostname
    cursor = db_conn.cursor()

    # hard coding the username of the container for the timebeing
    username = "user"

    # Need to check if the hostname already exists - then we are just udpdating - Determine the connection_id
    cursor.execute(
        "SELECT connection_id FROM guacamole_connection WHERE connection_name = %s AND parent_id IS NULL;",
        (hostname,),
    )
    connection_id = cursor.fetchone()

    if connection_id is None:
        logger.error(
            "Cannot update connection as it doesn't exist - use create",
            connection_name=con_name,
        )
    else:
        logger.info(
            "Connection ID already exists",
            con_name=con_name,
            conneciton_id=connection_id[0],
        )

        logger.info("Updating connection params")
        # Update entry
        cursor.execute(
            "UPDATE guacamole_connection_parameter SET parameter_value=%s WHERE connection_id=%s AND parameter_name='hostname';",
            (hostname, connection_id[0]),
        )
        cursor.execute(
            "UPDATE guacamole_connection_parameter SET parameter_value=%s WHERE connection_id=%s AND parameter_name='port';",
            (port, connection_id[0]),
        )
        cursor.execute(
            "UPDATE guacamole_connection_parameter SET parameter_value=%s WHERE connection_id=%s AND parameter_name='username';",
            (username, connection_id[0]),
        )
        cursor.execute(
            "UPDATE guacamole_connection_parameter SET parameter_value=%s WHERE connection_id=%s AND parameter_name='password';",
            (password, connection_id[0]),
        )
        cursor.execute(
            "UPDATE guacamole_connection_parameter SET parameter_value='true' WHERE connection_id=%s AND parameter_name='ignore-cert';",
            (connection_id[0],),
        )

    # Close communication with the database
    cursor.close()

    return True


def join_connection_to_user(username, hostname):

    cursor = db_conn.cursor()

    entity_id = get_user_entity_id(username)
    connection_id = get_connection_id(hostname)

    cursor.execute(
        "SELECT entity_id from guacamole_connection_permission where entity_id=%s AND connection_id=%s;",
        (entity_id, connection_id),
    )
    connection_map_exists = cursor.fetchone()

    if connection_map_exists is None:
        cursor.execute(
            "INSERT INTO guacamole_connection_permission (entity_id, connection_id, permission) \
                        VALUES (%s, %s, 'READ');",
            (entity_id, connection_id),
        )
    else:
        logger.error("Connection map already exists")

    # Close communication with the database
    cursor.close()

    return True


def delete_connection(username, hostname):
    try:
        con_name = hostname
        cursor = db_conn.cursor()

        # hard coding the username of the container for the timebeing
        username = "user"

        # Need to check if the hostname already exists - then we are just updating - Determine the connection_id
        cursor.execute(
            "SELECT connection_id FROM guacamole_connection WHERE connection_name = %s AND parent_id IS NULL;",
            (hostname,),
        )
        connection_id = cursor.fetchone()

        print(connection_id)

        if connection_id is None:
            logger.info("Connection does not exist", con_name=con_name)
            return False

        rows_deleted = 0

        cursor.execute("DELETE FROM guacamole_connection WHERE connection_id = %s", (connection_id,))

        rows_deleted = cursor.rowcount

        cursor.close()

    except (Exception, psycopg2.DatabaseError) as error:
        logger.error("Error deleting connection", error=errror)

    return rows_deleted
