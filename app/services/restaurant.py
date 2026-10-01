from typing import Sequence

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.dto.place import Place
from app.models.restaurant import Restaurant
from app.core.dependencies import places_client
from app.utils import db_helper


def get_restaurants(db: Session, cuisine: str, location: str) -> list[Restaurant]:
    all_saved = db.scalars(select(Restaurant)).all()
    db_results = [r for r in all_saved if cuisine in r.cuisine]

    remaining = max(0, 10 - len(db_results))
    if remaining == 0:
        return db_results

    saved_ids = {r.place_id for r in all_saved}
    places = places_client.search_restaurants(cuisine, location, remaining).places

    # Places can return restaurants we already saved (e.g. under another cuisine)
    new_restaurants = [_place_to_restaurant(p, cuisine) for p in places if p.id not in saved_ids]
    db_helper.save_all(db, *new_restaurants)

    already_saved = [r for r in all_saved if r.place_id in {p.id for p in places} and r not in db_results]
    return db_results + already_saved + new_restaurants


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
