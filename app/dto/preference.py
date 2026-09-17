from pydantic import BaseModel


class UserPreferences(BaseModel):
    top_cuisines: list[str]
    price_tier: int
    has_enough_data: bool