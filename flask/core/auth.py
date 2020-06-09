import json

from functools import wraps

import jwt
import os
import sys

from werkzeug.exceptions import HTTPException
from flask import abort

from flask import session
from flask import redirect
from flask import request

from core.log import logger


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        if "profile" in session:
            if username in session["profile"]:
                return f(*args, **kwargs)
        else:
            session["profile"] = {}

        headers = dict(request.headers)

        if "X-Auth-Username" not in headers:
            raise abort(403, description="Not Authenticated")

        session["profile"]["username"] = headers["X-Auth-Username"]

        return f(*args, **kwargs)

    return decorated


def is_admin(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        headers = dict(request.headers)

        if "X-Auth-Groups" not in headers:
            raise abort(403, description="Not Authenticated")

        groups = headers["X-Auth-Groups"].split(",")

        if "admin" not in groups:
            raise abort(403, description="Not an admin")

        return f(*args, **kwargs)

    return decorated


def decode_jwt(auth_token, aud):

    try:
        PUBLIC_KEY = os.getenv("PUBLIC_KEY", "RSA Public Key")
        aud = aud.split(",")
        payload = jwt.decode(auth_token, PUBLIC_KEY, audience=aud)

        return "verified"
    except:
        return "verification failed with - %s" % sys.exc_info()[0]
