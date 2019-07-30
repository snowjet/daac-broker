from datetime import datetime, timedelta

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jwt import PyJWTError
from passlib.context import CryptContext

from starlette.status import HTTP_401_UNAUTHORIZED

from app.db.db_utils import db
from app.oc.OpenShiftClient import GuacOpenShiftAccess
from app.core.log import logger
from app.core.config import JWT_TOKEN_PREFIX
from app.core.security import generate_password, hash_password, generate_session_secret

from app.models.token import Token, TokenData
from app.models.user import User, UserInDB


SECRET_KEY = generate_session_secret(32)
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Use External Source for this. Currently temp lookup

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/token")

fake_users_db = {
    "user": {
        "username": "user",
        "full_name": "John Doe",
        "email": "user@example.com",
        "hashed_password": "$2b$12$EixZaYVK1fsbw1ZfbX3OXePaWxn96p36WQoeG6Lruj3vjPGga31lW",
        "disabled": False,
        "role": "user",
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


def authenticate_user(username: str, password: str):
    userDB = fake_users_db
    user = _get_user(userDB, username)
    if not user:
        return False
    if not _verify_password(password, user.hashed_password):
        return False
    return user


def create_access_token(*, data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except PyJWTError:
        raise credentials_exception
    user = _get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def is_current_user_admin(current_user: User = Depends(get_current_user)):
    logger.info("checking if user is admin")

    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    if current_user.role.lower() != "admin":
        raise HTTPException(status_code=400, detail="Not an admin")

    logger.debug("User has role admin", user=current_user.username)
    return current_user


def _verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def _get_password_hash(password):
    return pwd_context.hash(password)


def _get_user(userDB, username: str):
    if username in userDB:
        user_dict = db[username]
        return UserInDB(**user_dict)
