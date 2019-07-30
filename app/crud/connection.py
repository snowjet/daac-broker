from asyncpg import Connection
from pydantic import EmailStr

from app.models.user import UserInCreate, UserInDB, UserInUpdate


async def get_user(conn: Connection, username: str) -> UserInDB:
    row = await conn.fetchrow(
        """
        SELECT id, username, email, salt, hashed_password, bio, image, created_at, updated_at
        FROM users
        WHERE username = $1
        """,
        username,
    )
    if row:
        return UserInDB(**row)


async def get_user_by_email(conn: Connection, email: EmailStr) -> UserInDB:
    row = await conn.fetchrow(
        """
        SELECT id, username, email, salt, hashed_password, bio, image, created_at, updated_at
        FROM users
        WHERE email = $1
        """,
        email,
    )
    if row:
        return UserInDB(**row)


async def create_user(conn: Connection, user: UserInCreate) -> UserInDB:
    dbuser = UserInDB(**user.dict())
    dbuser.change_password(user.password)

    row = await conn.fetchrow(
        """
        INSERT INTO users (username, email, salt, hashed_password, bio, image) 
        VALUES ($1, $2, $3, $4, $5, $6)
        RETURNING id, created_at, updated_at
        """,
        dbuser.username,
        dbuser.email,
        dbuser.salt,
        dbuser.hashed_password,
        dbuser.bio,
        dbuser.image,
    )

    dbuser.id = row["id"]
    dbuser.created_at = row["created_at"]
    dbuser.updated_at = row["updated_at"]

    return dbuser


async def update_user(conn: Connection, username: str, user: UserInUpdate) -> UserInDB:
    dbuser = await get_user(conn, username)

    dbuser.username = user.username or dbuser.username
    dbuser.email = user.email or dbuser.email
    dbuser.bio = user.bio or dbuser.bio
    dbuser.image = user.image or dbuser.image
    if user.password:
        dbuser.change_password(user.password)

    updated_at = await conn.fetchval(
        """
        UPDATE users
        SET username = $1, email = $2, salt = $3, hashed_password = $4, bio = $5, image = $6
        WHERE username = $7
        RETURNING updated_at
        """,
        dbuser.username,
        dbuser.email,
        dbuser.salt,
        dbuser.hashed_password,
        dbuser.bio,
        dbuser.image,
        username,
    )

    dbuser.updated_at = updated_at
    return dbuser
    

def _get_connection_id(self, hostname):

    cursor = self.db_conn.cursor()

    cursor.execute(
        "SELECT connection_id from guacamole_connection where connection_name=%s;",
        (hostname,),
    )
    connection_id = cursor.fetchone()

    # Close communication with the database
    cursor.close()

    return connection_id


def create_connection(self, username, hostname, password, protocol="rdp", port="3389"):
    con_name = hostname
    cursor = self.db_conn.cursor()

    # Need to check if the hostname already exists - then we are just udpdating - Determine the connection_id
    cursor.execute(
        "SELECT connection_id FROM guacamole_connection WHERE connection_name = %s AND parent_id IS NULL;",
        (hostname,),
    )
    connection_id = cursor.fetchone()

    if connection_id is None:
        logger.info("Adding new connection", name=con_name)

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
    else:
        logger.error(
            "Connection ID already exists - use update",
            name=con_name,
            conneciton_id=connection_id[0],
        )

    cursor.close()

    return True


def update_connection(self, username, hostname, password, protocol="rdp", port="3389"):
    con_name = hostname
    cursor = self.db_conn.cursor()

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
            name=con_name,
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

    # Close communication with the database
    cursor.close()

    return True


def join_connection_to_user(self, username, hostname):

    cursor = self.db_conn.cursor()

    entity_id = self._get_user_identity(username)
    connection_id = self._get_connection_id(hostname)

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
        log.error("Connection map already exists")

    # Close communication with the database
    cursor.close()

    return True
