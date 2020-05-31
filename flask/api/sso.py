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

from core.config import sso_config, GUAC_URL

from core.auth import requires_auth
from core.log import logger

from crud.connection import get_connections
from crud.user_conn import create_user_and_connection, delete_connection_for_user

def create_sso_blueprint(oauth):

    auth_blueprint = Blueprint("auth", __name__)
    auth_blueprint.secret_key = sso_config["SECRET_KEY"]

    sso_oauth = oauth.register(
        "sso",
        client_id=sso_config["client_id"],
        client_secret=sso_config["client_secret"],
        server_metadata_url=f"{sso_config['sso_url']}/.well-known/openid-configuration",
        client_kwargs={"scope": "openid profile email"},
    )

    # Here we're using the /callback route.
    @auth_blueprint.route("/callback")
    def callback_handling():
        # Handles response from token endpoint
        sso_oauth.authorize_access_token()
        resp = sso_oauth.get("userinfo")
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
        return sso_oauth.authorize_redirect(
            redirect_uri=f"{sso_config['daac_redirect_domain']}/callback",
            audience=f"https://{sso_config['sso_oauth_domain']}/userinfo",
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
        # Redirect user to logout endpoint and then back to the home
        params = {
            "returnTo": f"{sso_config['daac_redirect_domain']}",
            "client_id": sso_config["client_id"],
        }
        return redirect(sso_oauth.api_base_url + "/v2/logout?" + urlencode(params))

    return auth_blueprint
