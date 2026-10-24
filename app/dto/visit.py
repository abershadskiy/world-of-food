
import datetime
from datetime import date
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator

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

    @field_validator("date")
    @classmethod
    def date_cannot_be_cleared(cls, value):
        # Leaving date out keeps it as is, but the column can't be empty
        if value is None:
            raise ValueError("date can't be null")
        return value


class Visit(VisitBase):
    id: int
    restaurant: Restaurant
    model_config = ConfigDict(from_attributes=True)
