from core.log import logger
from core.security import generate_password, hash_password
from crud.connection import create_connection, join_connection_to_user
from crud.openshift import create_user_daac
from crud.user import add_user_to_db
from models.user import User, UserCreds

from flask import Blueprint
from flask import session

from core.auth import requires_auth

users_blueprint = Blueprint("users_blueprint", __name__)

# User Functions
@users_blueprint.route(
    "/user", methods=["GET", "POST", "PATCH", "PUT", "DELETE"]
)
@requires_auth
def read_user_me():
    userinfo = session['profile']

    return userinfo['name']

@users_blueprint.route(
    "/user/connection", methods=["GET"]
)
@requires_auth
def read_user_me_connection():
    connections = {}
    return connections

@users_blueprint.route("/user/connection/create", methods=["POST"])
@requires_auth
def user_create_connection():
    connections = {} 
    return connections


@users_blueprint.route("/user/connection/delete", methods=["POST", "DELETE"])
@requires_auth
def user_delete_connection():
    connections = {} 
    return connections

