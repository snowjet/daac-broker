from core.log import logger
from core.security import generate_password, hash_password
from crud.connection import create_connection, join_connection_to_user
from crud.openshift import create_user_daac
from crud.user import add_user_to_db
from db.db_utils import load_schema_safe
from models.user import User, UserCreds

from flask import Blueprint

from core.auth import requires_auth, is_admin

admin_blueprint = Blueprint("admin_blueprint", __name__)

# Admin Functions
@admin_blueprint.route(
    "/admin/prepare-db", methods=["GET", "POST", "PATCH", "PUT", "DELETE"]
)
@requires_auth
@is_admin
def prepare_db():

    msg = load_schema_safe()

    return {"prepare-db": msg}


@admin_blueprint.route("/admin/list-users/", methods=["GET"])
@requires_auth
@is_admin
def list_users():

    msg = "tst"
    return {"users:", msg}


@admin_blueprint.route("/admin/get-user/{username}", methods=["GET"])
@requires_auth
@is_admin
def get_user():

    msg = "tst"

    return {"users:", msg}


@admin_blueprint.route("/admin/add-user/{username}", methods=["PUT"])
@requires_auth
@is_admin
def add_user(username: str, user_creds: UserCreds):

    hostname = f"desktop-{username}"

    password = user_creds.password

    rdp_password = generate_password()
    password_hash = hash_password(password=rdp_password)

    add_user_to_db(username, password)
    create_connection(username, hostname, password=rdp_password)
    join_connection_to_user(username, hostname)

    dc_msg, svc_msg = create_user_daac(username, password_hash)

    logger.info("Attempted to create user", user=username, dc=dc_msg, svc=svc_msg)

    return {"user-added": username}
