from datetime import date
from typing import List, Optional

from pydantic import BaseModel, ConfigDict


class RestaurantBase(BaseModel):
    name: str
    cuisine: list[str]
    price_tier: Optional[int] = None
    city: Optional[str] = None
    notes: Optional[str] = None
    place_id: Optional[str]
    place_lat: Optional[float]
    place_long: Optional[float]


class RestaurantCreate(RestaurantBase):
    pass


class Restaurant(RestaurantBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

