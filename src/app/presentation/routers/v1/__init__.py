from fastapi import APIRouter

from app.presentation.routers.v1.users import router as users_router

router = APIRouter()
router.include_router(users_router, prefix="/v1")
