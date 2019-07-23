
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, Header
from starlette.exceptions import HTTPException
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

import jwt
from app.crud.user import get_user
from app.db.database import DataBase, get_database
from app.models.token import TokenPayload
from app.models.user import User
from jwt import PyJWTError

from .config import JWT_TOKEN_PREFIX, SECRET_KEY

ALGORITHM = "HS256"
access_token_jwt_subject = "access"