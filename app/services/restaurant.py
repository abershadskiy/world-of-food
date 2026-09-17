from typing import Sequence

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.dto.place import Place
from app.models.restaurant import Restaurant
from app.core.dependencies import places_client
from app.utils import db_helper


def get_restaurants(db: Session, cuisine: str, location: str) -> list[Restaurant]:
    db_results = db.scalars(select(Restaurant)).all()
    db_results = [r for r in db_results if cuisine in r.cuisine]

    remaining = max(0, 10 - len(db_results))

    if remaining == 0:
        place_results = []
    else:
        place_results = [_place_to_restaurant(place, cuisine) for place in
                         places_client.search_restaurants(cuisine, location, remaining).places]
        db_helper.save_all(db, *place_results)

    return list(db_results) + list(place_results)






# Helpers

def _place_to_restaurant(place: Place, fallback_cuisine: str) -> Restaurant:
    return Restaurant(
        place_id=place.id,
        cuisine=_extract_cuisines(place.types, fallback_cuisine),
        price_tier=_tier_to_number(place.price_level),
        place_long=place.location.longitude,
        place_lat=place.location.latitude,
        name=place.display_name.text
    )


def _extract_cuisines(types: list[str], fallback_cuisine: str) -> list[str]:
    restaurant_types = [t for t in types if t.endswith("_restaurant")]
    if not restaurant_types:
        return [fallback_cuisine]
    else:
        return [rt.removesuffix("_restaurant") for rt in restaurant_types]


def _tier_to_number(tier: str) -> int:
    mappings = {
        "PRICE_LEVEL_UNSPECIFIED": -1,
        "PRICE_LEVEL_FREE": 0,
        "PRICE_LEVEL_INEXPENSIVE": 1,
        "PRICE_LEVEL_MODERATE": 2,
        "PRICE_LEVEL_EXPENSIVE": 3,
        "PRICE_LEVEL_VERY_EXPENSIVE": 4
    }
    return mappings[tier]
