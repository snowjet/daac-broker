from fastapi import APIRouter

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
def get_root():

    msg = "tst"
    return {"users:", msg}

