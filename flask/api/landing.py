from functools import wraps
import json
from os import environ as env
from werkzeug.exceptions import HTTPException

from dotenv import load_dotenv, find_dotenv

from flask import Blueprint
from flask import Flask
from flask import jsonify
from flask import redirect
from flask import render_template
from flask import session
from flask import url_for
from flask import request, flash

from six.moves.urllib.parse import urlencode

from core.config import sso_config, GUAC_URL

from core.auth import requires_auth
from core.log import logger

from crud.connection import get_connections
from crud.user_conn import create_user_and_connection, delete_connection_for_user


landing_blueprint = Blueprint("landing_blueprint", __name__)

@landing_blueprint.route("/", methods=["GET", "POST"])
@requires_auth
def dashboard():
    username = session["profile"]["username"]

    if request.method == "POST":
        if request.form["submit"] == "create_new_conn":
            logger.info("Create Connection Started for user:", username=username)
            msg = create_user_and_connection(username)

            flash("DaaC Creation Started")

        elif request.form["submit"] == "delete_conn":
            logger.info("Delete Connection Started for user:", username=username)

            msg = delete_connection_for_user(username)
            flash("Delete DaaC Started")

    connections = get_connections(username)

    if len(connections) == 0:
        connections = None
        print("dict1 is Empty")    

    logger.debug("Connections", connection=connections, GUAC_URL=GUAC_URL)

    return render_template(
        "landing.html",
        userinfo=session["profile"],
        userinfo_pretty=json.dumps(session["jwt_payload"], indent=4),
        connections=connections,
        GUAC_URL=GUAC_URL,
    )

@landing_blueprint.route("/logout")
def logout():
    # Clear session stored data
    session.clear()
    # Redirect user to logout endpoint and then back to the home

    return redirect("/oauth/logout?" + "/")

