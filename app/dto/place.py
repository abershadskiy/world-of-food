from enum import Enum

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CamelCaseModel(BaseModel):
    model_config = ConfigDict(alias_generator=to_camel, populate_by_name=True)

class DisplayName(CamelCaseModel):
    text: str

class PriceLevel(str, Enum):
    PRICE_LEVEL_FREE = "PRICE_LEVEL_FREE"
    PRICE_LEVEL_UNSPECIFIED = "PRICE_LEVEL_UNSPECIFIED"
    PRICE_LEVEL_INEXPENSIVE = "PRICE_LEVEL_INEXPENSIVE"
    PRICE_LEVEL_MODERATE = "PRICE_LEVEL_MODERATE"
    PRICE_LEVEL_EXPENSIVE = "PRICE_LEVEL_EXPENSIVE"
    PRICE_LEVEL_VERY_EXPENSIVE = "PRICE_LEVEL_VERY_EXPENSIVE"

class Location(CamelCaseModel):
    latitude: float
    longitude: float

class Place(CamelCaseModel):
    display_name: DisplayName
    id: str
    price_level: PriceLevel = PriceLevel.PRICE_LEVEL_UNSPECIFIED
    location: Location
    types: list[str]

class PlaceResult(CamelCaseModel):
    place: Place

class PlaceResults(CamelCaseModel):
    places: list[Place]