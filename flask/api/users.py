from core.log import logger
from crud.connection import get_connections
from crud.user_conn import create_user_and_connection
from models.user import User, UserCreds

from flask import Blueprint
from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from flask import request, flash

from wtforms import Form, TextField, TextAreaField, validators, StringField, SubmitField


from core.auth import requires_auth
from core.config import GUAC_URL

import json

users_blueprint = Blueprint("users_blueprint", __name__)


# User Functions
@users_blueprint.route("/users", methods=["GET", "POST", "PATCH", "PUT", "DELETE"])
@requires_auth
def read_user_me():
    userinfo = session["profile"]

    return userinfo["name"]


@users_blueprint.route("/users/connection", methods=["GET", "POST"])
@requires_auth
def user_connection():

    username = session["profile"]["name"]

    if request.method == "POST":
        if request.form["submit"] == "create_new_conn":
            logger.info("Create Connection Started for user:", username=username)
            msg = create_user_and_connection(username)

            flash("Connection Creation Started")

    connections = get_connections(username)

    logger.debug("Connections", connection=connections, GUAC_URL=GUAC_URL)

    return render_template(
        "connections.html", userinfo=session["profile"], connections=connections, GUAC_URL=GUAC_URL
    )


@users_blueprint.route("/users/connection/delete", methods=["POST", "DELETE"])
@requires_auth
def user_delete_connection():
    connections = {}
    return connections
