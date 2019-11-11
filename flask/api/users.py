from core.log import logger
from core.security import generate_password, hash_password
from crud.connection import create_connection, join_connection_to_user, get_connections
from crud.openshift import create_user_daac
from crud.user import add_user_to_db
from models.user import User, UserCreds

from flask import Blueprint
from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for

from core.auth import requires_auth

users_blueprint = Blueprint("users_blueprint", __name__)

# User Functions
@users_blueprint.route(
    "/users", methods=["GET", "POST", "PATCH", "PUT", "DELETE"]
)
@requires_auth
def read_user_me():
    userinfo = session['profile']

    return userinfo['name']

@users_blueprint.route(
    "/users/connection", methods=["GET"]
)
@requires_auth
def read_user_my_connection():

    connections = {}
    connections['0'] = {'name': "desktop", 'url': 'https://guac'}
    connections['1'] = {'name': "desktop2", 'url': 'https://guac2'}

    print(connections)

    for conn in connections:
        logger.debug("Connection Vars", connections=connections[conn])

    return render_template(
        "connections.html",
        userinfo=session["profile"],
        connections=connections,
    )

@users_blueprint.route("/users/connection/create", methods=["POST"])
@requires_auth
def user_create_connection():

    username = session['profile']['name']

    hostname = f"desktop-{username}"

    # Set password to None if using Auth0 backend
    password = None

    rdp_password = generate_password()
    password_hash = hash_password(password=rdp_password)

    add_user_to_db(username, password)
    create_connection(username, hostname, password=rdp_password)
    join_connection_to_user(username, hostname)

    dc_msg, svc_msg = create_user_daac(username, password_hash)

    logger.info("Attempted to create user", user=username, dc=dc_msg, svc=svc_msg)

    return {"user-added": username}

    connections = {} 
    return connections


@users_blueprint.route("/users/connection/delete", methods=["POST", "DELETE"])
@requires_auth
def user_delete_connection():
    connections = {} 
    return connections

