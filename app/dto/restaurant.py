from pydantic import BaseModel, ConfigDict


class RestaurantBase(BaseModel):
    name: str
    cuisine: list[str]
    price_tier: int = -1
    place_id: str
    place_lat: float
    place_long: float
    address: str | None = None
    city: str | None = None
    region: str | None = None
    country: str | None = None


class RestaurantCreate(RestaurantBase):
    pass


class Restaurant(RestaurantBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
