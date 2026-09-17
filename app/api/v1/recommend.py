from fastapi import APIRouter

from app.api.main_router import router

recommend_router = APIRouter(
    prefix="/recommend",
    tags=["recommend"]
)

@router.get("/")
def x():
    return None