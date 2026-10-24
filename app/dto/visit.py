
from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.dto.restaurant import Restaurant


class VisitBase(BaseModel):
    restaurant_id: int
    date: date
    rating: Optional[int] = None
    notes: Optional[str] = None


class VisitCreate(VisitBase):
    pass


class Visit(VisitBase):
    id: int
    restaurant: Restaurant
    model_config = ConfigDict(from_attributes=True)
