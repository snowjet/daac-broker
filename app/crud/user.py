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


def _get_user_id(self, entity_id):

    cursor = self.db_conn.cursor()

    # Execute a command: this creates a new table

    cursor.execute(
        "SELECT user_id from guacamole_user where entity_id=%s;", (entity_id,)
    )
    user_id = cursor.fetchone()

    # Close communication with the database
    cursor.close()

    return user_id


def _get_user_identity(self, username):

    cursor = self.db_conn.cursor()

    # Execute a command: this creates a new table
    cursor.execute("SELECT entity_id from guacamole_entity where name=%s;", (username,))
    entity_id = cursor.fetchone()

    # Close communication with the database
    cursor.close()

    return entity_id


def add_user(self, username, password):

    cursor = self.db_conn.cursor()

    # ensure salt hash is uppercase when stored in postgres - guacamole client requires this - NFI
    salt = uuid.uuid4()
    salt_hash = hashlib.sha256(salt.bytes).hexdigest()
    salt_hash_upper = salt_hash.upper()
    password_hash = hashlib.sha256(
        "".join((password, salt_hash_upper)).encode("UTF-8")
    ).hexdigest()
    logger.debug("Salt Hash", salt_hash_upper=salt_hash_upper)
    logger.debug("Password Hash", password_hash=password_hash)

    entity_id = self._get_user_identity(username)
    if entity_id is None:

        logger.info(
            "Did not receive entity id for user, adding user", username=username
        )

        # add user to entity table
        cursor.execute(
            "INSERT INTO guacamole_entity (name, type) VALUES (%s, 'USER');",
            (username,),
        )
        entity_id = self._get_user_identity(username)

        cursor.execute(
            "INSERT INTO guacamole_user (entity_id, password_hash, password_salt, password_date) \
                        SELECT entity_id, decode(%s, 'hex'), decode(%s, 'hex'), CURRENT_TIMESTAMP \
                        FROM guacamole_entity WHERE name = %s AND guacamole_entity.type = 'USER';",
            (password_hash, salt_hash, username),
        )

        cursor.execute(
            "INSERT INTO guacamole_user_permission (entity_id, affected_user_id, permission) \
                        SELECT guacamole_entity.entity_id, guacamole_user.user_id, permission::guacamole_object_permission_type \
                        FROM (VALUES (%s, %s, 'READ')) permissions (username, affected_username, permission) \
                        JOIN guacamole_entity          ON permissions.username = guacamole_entity.name AND guacamole_entity.type = 'USER' \
                        JOIN guacamole_entity affected ON permissions.affected_username = affected.name AND guacamole_entity.type = 'USER' \
                        JOIN guacamole_user            ON guacamole_user.entity_id = affected.entity_id;",
            (username, username),
        )

    else:
        logger.info("Retrieved entity id for user", username=username)

    # Close communication with the database
    cursor.close()

    return True

