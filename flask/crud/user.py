import hashlib
import uuid

from core.log import logger
from db.db_utils import get_database_connection

db_conn = get_database_connection()


def add_admin_to_user(username):

    cursor = db_conn.cursor()

    cursor.execute(
        "INSERT INTO guacamole_system_permission (entity_id, permission) \
            SELECT entity_id, permission::guacamole_system_permission_type \
            FROM ( \
            VALUES \
            ('%s', 'CREATE_CONNECTION'), \
            ('%s', 'CREATE_CONNECTION_GROUP'), \
            ('%s', 'CREATE_SHARING_PROFILE'), \
            ('%s', 'CREATE_USER'), \
            ('%s', 'CREATE_USER_GROUP'), \
            ('%s', 'ADMINISTER') \
    ) permissions (username, permission) \
    JOIN guacamole_entity ON permissions.username = guacamole_entity.name AND guacamole_entity.type = 'USER';",
        (username),
    )

    return True


def create_password_hash(password):

    if password is None:
        logger.error("Password not passed for user", username=username)
        return False

    # ensure salt hash is uppercase when stored in postgres - guacamole client requires this - NFI
    salt = uuid.uuid4()
    salt_hash = hashlib.sha256(salt.bytes).hexdigest()
    salt_hash_upper = salt_hash.upper()
    password_hash = hashlib.sha256(
        "".join((str(password), str(salt_hash_upper))).encode("UTF-8")
    ).hexdigest()
    logger.debug("Salt Hash", salt_hash_upper=salt_hash_upper)
    logger.debug("Password Hash", password_hash=password_hash)

    return password_hash, salt_hash


def get_user_id(entity_id):

    cursor = db_conn.cursor()

    # Execute a command: this creates a new table

    cursor.execute(
        "SELECT user_id from guacamole_user where entity_id=%s;", (entity_id,)
    )
    user_id = cursor.fetchone()

    # Close communication with the database
    cursor.close()

    return user_id


def get_user_entity_id(username):

    cursor = db_conn.cursor()

    # Execute a command: this creates a new table
    cursor.execute("SELECT entity_id from guacamole_entity where name=%s;", (username,))
    entity_id = cursor.fetchone()

    # Close communication with the database
    cursor.close()

    return entity_id


def add_user_to_db(username, password):

    cursor = db_conn.cursor()

    if password is None:
        password = uuid.uuid4()

    password_hash, salt_hash = create_password_hash(password)

    entity_id = get_user_entity_id(username)
    if entity_id is None:

        logger.info(
            "Did not receive entity id for user, adding user", username=username
        )

        # add user to entity table
        cursor.execute(
            "INSERT INTO guacamole_entity (name, type) VALUES (%s, 'USER');",
            (username,),
        )
        entity_id = get_user_entity_id(username)

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


def update_users_db_password(username, password):

    cursor = db_conn.cursor()

    if password is None:
        logger.error("Password not passed for user", username=username)
        return False

    password_hash, salt_hash = create_password_hash(password)

    entity_id = get_user_entity_id(username)
    if entity_id is None:
        logger.error("User does not exist, wont update password", username=username)
    else:
        logger.info("Retrieved entity id for user", username=username)

        # update user to entity table
        cursor.execute(
            "INSERT INTO guacamole_user (entity_id, password_hash, password_salt, password_date) \
                        SELECT entity_id, decode(%s, 'hex'), decode(%s, 'hex'), CURRENT_TIMESTAMP \
                        FROM guacamole_entity WHERE name = %s AND guacamole_entity.type = 'USER' \
            ON CONFLICT (entity_id) \
                DO UPDATE \
                SET entity_id = %s, password_hash = decode(%s, 'hex'),  password_salt = decode(%s, 'hex');",
            (password_hash, salt_hash, username, entity_id, password_hash, salt_hash),
        )

    # Close communication with the database
    cursor.close()

    return True
