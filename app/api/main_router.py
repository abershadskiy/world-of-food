from fastapi import APIRouter

from app.api.v1 import restaurant, user

router = APIRouter(
    prefix="/v1"
)
router.include_router(restaurant.router)
router.include_router(user.router)

