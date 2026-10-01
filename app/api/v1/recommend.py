from fastapi import APIRouter

router = APIRouter(
    prefix="/recommend",
    tags=["recommend"]
)


@router.get("/")
def get_recommendations():
    return None
