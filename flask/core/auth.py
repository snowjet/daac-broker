from functools import wraps
import json
from os import environ as env
from werkzeug.exceptions import HTTPException
from flask import abort

from flask import session
from flask import redirect

from core.log import logger
from core.authman import Auth0Management
from models.user import User, UserInDB

auth0_mgmt = Auth0Management()

def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "profile" not in session:
            # Redirect to Login page here
            return redirect("/")
        return f(*args, **kwargs)

    return decorated


def is_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        userinfo = session["profile"]

        if not auth0_mgmt.is_admin(userinfo['name']):
            raise abort(403, description="Not an admin")
            return redirect("/")

        return f(*args, **kwargs)

    return decorated
