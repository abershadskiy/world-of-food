
import datetime
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


class VisitUpdate(BaseModel):
    # datetime.date, because a bare `date` here would mean the field itself (None), not the type
    date: Optional[datetime.date] = None
    rating: Optional[int] = None
    notes: Optional[str] = None


class Visit(VisitBase):
    id: int
    restaurant: Restaurant
    model_config = ConfigDict(from_attributes=True)
