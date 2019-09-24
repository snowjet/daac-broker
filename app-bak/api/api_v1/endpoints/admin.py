from fastapi import APIRouter, Depends

from core.jwt import get_current_active_user, is_current_user_admin
from core.log import logger
from core.security import generate_password, hash_password
from crud.connection import create_connection, join_connection_to_user
from crud.openshift import create_user_daac
from crud.user import add_user_to_db
from db.db_utils import load_schema_safe
from models.user import User, UserCreds

router = APIRouter()

# Admin Functions
@router.put("/admin/prepare-db")
async def prepare_db(current_user: User = Depends(is_current_user_admin)):

    msg = load_schema_safe()

    return {"prepare-db": msg}


@router.get("/admin/list-users/")
def list_users():

    msg = "tst"
    return {"users:", msg}


@router.get("/admin/get-user/{username}")
def get_user():

    msg = "tst"

    return {"users:", msg}


@router.put("/admin/add-user/{username}")
def add_user(
    username: str,
    user_creds: UserCreds,
    current_user: User = Depends(is_current_user_admin),
):

    hostname = f"desktop-{username}"
    password = user_creds.password

    rdp_password = generate_password()
    password_hash = hash_password(password=rdp_password)

    add_user_to_db(username, password)
    create_connection(username, hostname, password=rdp_password)
    join_connection_to_user(username, hostname)

    dc_msg, svc_msg = create_user_daac(username, password_hash)

    logger.info("Attempted to create user", user=username, dc=dc_msg, svc=svc_msg)

    return {"user-added": username}
