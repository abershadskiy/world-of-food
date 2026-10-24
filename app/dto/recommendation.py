from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

from app.dto.restaurant import Restaurant
from app.models.recommendation import Action


class Recommendation(BaseModel):
    id: int
    restaurant: Restaurant
    action: Optional[Action] = None
    action_timestamp: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class RecommendationAction(BaseModel):
    action: Action
