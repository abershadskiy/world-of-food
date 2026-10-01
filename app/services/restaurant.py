from typing import Sequence

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.dto.place import Place
from app.models.restaurant import Restaurant
from app.core.dependencies import places_client
from app.utils import db_helper


def get_restaurants(db: Session, cuisine: str, location: str) -> list[Restaurant]:
    all_saved = db.scalars(select(Restaurant)).all()
    matching = [r for r in all_saved if cuisine in r.cuisine]

    remaining = max(0, 10 - len(matching))
    if remaining == 0:
        return matching

    saved_by_place_id = {r.place_id: r for r in all_saved}
    places = places_client.search_restaurants(cuisine, location, remaining).places

    # Places can return restaurants we already saved (e.g. under another cuisine),
    # so only create rows for the ones we haven't seen
    results = list(matching)
    new_restaurants = []
    for place in places:
        if place.id in saved_by_place_id:
            saved = saved_by_place_id[place.id]
            if saved not in results:
                results.append(saved)
        else:
            new_restaurants.append(_place_to_restaurant(place, cuisine))

    db_helper.save_all(db, *new_restaurants)
    return results + new_restaurants


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
