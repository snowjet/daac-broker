from fastapi import APIRouter, Depends

from app.core.jwt import get_current_active_user
from app.crud.user import update_user
from app.db.db_utils import db
from app.models.user import User

router = APIRouter()

@router.get("/users/me/", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return {"current_user": current_user}
