
from datetime import datetime, timedelta
from typing import Optional

from fastapi import Depends, Header
from starlette.exceptions import HTTPException
from starlette.status import HTTP_403_FORBIDDEN, HTTP_404_NOT_FOUND

import jwt

from jwt import PyJWTError
from app.crud.user import get_user
from db.database import DataBase, get_database
from app.models.token import TokenPayload
from app.models.user import User

from core.config import JWT_TOKEN_PREFIX, ACCESS_TOKEN_EXPIRE_MINUTES
from core.security import generate_password, hash_password, generate_session_secret

access_token_jwt_subject = "access"
SECRET_KEY = generate_session_secret(32)
ALGORITHM = "HS256"