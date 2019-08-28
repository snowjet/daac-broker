from fastapi import APIRouter, Depends
from core.jwt import oauth2_scheme

from .endpoints.admin import router as admin_router
from .endpoints.auth import router as auth_router

# from .endpoints.projects import router as projects_router
# from .endpoints.services import router as services_router
from .endpoints.users import router as user_router

router = APIRouter()

router.include_router(admin_router)
router.include_router(auth_router)
# router.include_router(projects_router)
# router.include_router(services_router)
router.include_router(user_router)


@router.get("/")
async def read_root(token: str = Depends(oauth2_scheme)):
    return {
        "Message": "Guac API Broker - connect to /docs for an API breakdown",
        "token": token,
    }
