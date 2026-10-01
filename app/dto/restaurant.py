from pydantic import BaseModel, ConfigDict


class RestaurantBase(BaseModel):
    name: str
    cuisine: list[str]
    price_tier: int | None = None
    place_id: str
    place_lat: float
    place_long: float


class RestaurantCreate(RestaurantBase):
    pass


class Restaurant(RestaurantBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
