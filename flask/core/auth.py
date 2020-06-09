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
from libgravatar import Gravatar


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):

        if "profile" in session:
            if "username" in session["profile"]:
                logger.debug("Session Profile Exists")
                return f(*args, **kwargs)
        else:
            logger.debug("No Session Profile - Create Profile")
            session["profile"] = {}

        headers = dict(request.headers)

        if "X-Auth-Username" not in headers:
            logger.debug("Missing Header X-Auth-Username")
            raise abort(403, description="Not Authenticated")

        session["profile"]["username"] = headers["X-Auth-Username"]

        if "picture" not in session["profile"]:
            if "X-Auth-Email" not in headers:
                logger.info("No email address provided, cannot lookup avatar")
                session["profile"]["email"] = ''
            else:
                logger.debug("Header X-Auth-Email", email=headers["X-Auth-Email"])
                session["profile"]["email"] = headers["X-Auth-Email"]

            g = Gravatar(session["profile"]["email"])
            session["profile"]["picture"] = g.get_image(size=40, default='mm', force_default=False)
            logger.debug("Avatar Lookup", picture=session["profile"]["picture"])            

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

        return "Verified"
    except:
        return "Verification failed with - %s" % sys.exc_info()[0]
