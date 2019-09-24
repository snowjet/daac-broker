from fastapi import APIRouter, Depends

from core.jwt import get_current_active_user
from models.user import User

router = APIRouter()


@router.get("/user", response_model=User)
async def read_user_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get("/user/update", response_model=User)
async def update_user_me(current_user: User = Depends(get_current_active_user)):
    return current_user


@router.get("/user/connection", response_model=User)
async def read_user_me_connection(
    current_user: User = Depends(get_current_active_user)
):
    return current_user


@router.get("/user/connection/update", response_model=User)
async def update_user_me_connection(
    current_user: User = Depends(get_current_active_user)
):
    return current_user
