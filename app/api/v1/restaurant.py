from typing import Sequence, Optional

from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from app.dto.restaurant import Restaurant
from app.services import restaurant
from app.core.database import get_db

router = APIRouter(
    prefix="/restaurants",
    tags=["restaurants"]
)


# @router.post("/restaurants", response_model=Restaurant)
# def create_restaurant(restaurant: dto.RestaurantCreate):
#     # return crud.create_restaurant(db, restaurant)
#     return None

@router.get("/", response_model=Sequence[Restaurant])
def get_restaurants(cuisine: str, location: str, db: Session = Depends(get_db)):
    return restaurant.get_restaurants(db, cuisine, location)
