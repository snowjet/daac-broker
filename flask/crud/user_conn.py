import hashlib

from core.log import logger

from core.security import generate_password, generate_linux_password_hash
from crud.connection import (
    create_connection,
    join_connection_to_user,
    get_connections,
    delete_connection,
)
from crud.openshift import create_daac, delete_daac
from crud.user import add_user_to_db


def _allowed_to_delete_daac(username, connection_name):

    connections = get_connections(username)

    for conn in connections:
        if connection_name in conn["connection_name"]:
            return True

    return False


def create_user_and_connection(username):

    username_digest = hashlib.md5(username.encode("utf-8")).hexdigest()

    hostname = f"desktop-{username_digest}"

    # Set password to None if using Auth0 backend
    password = None

    rdp_password = generate_password()
    password_hash = generate_linux_password_hash(password=rdp_password)

    add_user_to_db(username, password)
    create_connection(username, hostname, password=rdp_password)
    join_connection_to_user(username, hostname)

    dc_msg, svc_msg = create_daac(username, username_digest, password_hash)

    logger.info("Attempted to create user", user=username, dc=dc_msg, svc=svc_msg)

    return {"user-added": username}


def delete_connection_for_user(username):

    username_digest = hashlib.md5(username.encode("utf-8")).hexdigest()

    hostname = f"desktop-{username_digest}"

    if _allowed_to_delete_daac(username, hostname):
        logger.info("Attempting to Delete Connection", user=username)
        dc_msg, svc_msg = delete_daac(username, username_digest)

        rows = delete_connection(username, hostname)

        logger.info(
            "Attempted to Delete Connection", user=username, dc=dc_msg, svc=svc_msg
        )

    return True


def sync_password():
    # need to write a sync password field

    return True
