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

from authlib.integrations.flask_client import OAuth
from six.moves.urllib.parse import urlencode

from core.config import auth0_config, GUAC_URL

from core.auth import requires_auth
from core.log import logger

from crud.connection import get_connections
from crud.user_conn import create_user_and_connection, delete_connection_for_user


def create_auth0_blueprint(oauth):

    auth_blueprint = Blueprint("auth", __name__)
    auth_blueprint.secret_key = auth0_config["SECRET_KEY"]

    auth0 = oauth.register(
        "auth0",
        client_id=auth0_config["client_id"],
        client_secret=auth0_config["client_secret"],
        api_base_url=f"https://{auth0_config['auth0_domain']}",
        access_token_url=f"https://{auth0_config['auth0_domain']}/oauth/token",
        authorize_url=f"https://{auth0_config['auth0_domain']}/authorize",
        client_kwargs={"scope": "openid profile email"},
    )

    # Here we're using the /callback route.
    @auth_blueprint.route("/callback")
    def callback_handling():
        # Handles response from token endpoint
        auth0.authorize_access_token()
        resp = auth0.get("userinfo")
        userinfo = resp.json()

        # Store the user information in flask session.
        session["jwt_payload"] = userinfo
        session["profile"] = {
            "user_id": userinfo["sub"],
            "name": userinfo["name"],
            "picture": userinfo["picture"],
        }
        return redirect("/dashboard")

    @auth_blueprint.route("/login")
    def login():
        return auth0.authorize_redirect(
            redirect_uri=f"{auth0_config['daac_redirect_domain']}/callback",
            audience=f"https://{auth0_config['auth0_domain']}/userinfo",
        )

    @auth_blueprint.route("/dashboard", methods=["GET", "POST"])
    @requires_auth
    def dashboard():

        username = session["profile"]["name"]

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

    @auth_blueprint.route("/logout")
    def logout():
        # Clear session stored data
        session.clear()
        # Redirect user to logout endpoint
        params = {
            "returnTo": url_for("home", _external=True),
            "client_id": auth0_config["client_id"],
        }
        return redirect(auth0.api_base_url + "/v2/logout?" + urlencode(params))

    return auth_blueprint
