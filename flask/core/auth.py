from functools import wraps
import json
from os import environ as env
from werkzeug.exceptions import HTTPException
from flask import abort

from flask import session
from flask import redirect

from core.log import logger
from models.user import User, UserInDB


userDB = {
    "user": {
        "username": "user",
        "full_name": "John Doe",
        "email": "user@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
        "role": "user",
    },
    "john": {
        "username": "john",
        "full_name": "John Doe",
        "email": "user@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
        "role": "admin",
    },
    "admin": {
        "username": "admin",
        "full_name": "John Doe",
        "email": "admin@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
        "role": "admin",
    },
}


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

        user = _get_user(userDB, username=userinfo["name"])

        print(user)

        if user is None:
            raise abort(403, description="Not an admin")
            return redirect("/")

        if user.disabled:
            abort(403, description="Inactive user")
            return redirect("/")

        if user.role.lower() != "admin":
            raise abort(403, description="Not an admin")
            return redirect("/")

        return f(*args, **kwargs)

    return decorated


def _verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def _get_password_hash(password):
    return pwd_context.hash(password)


def _get_user(userDB, username: str):
    if username in userDB:
        user_dict = userDB[username]
        return UserInDB(**user_dict)
    
    return None
