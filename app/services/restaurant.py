from typing import Sequence

from sqlalchemy.orm import Session
from sqlalchemy import select

from app.dto.place import Place, PriceLevel, PRICE_LEVELS_BY_TIER
from app.models import Visit
from app.models.restaurant import Restaurant
from app.core.dependencies import places_client
from app.utils import db_helper


def get_restaurants(db: Session, cuisine: str, location: str) -> list[Restaurant]:
    all_saved = db.scalars(select(Restaurant)).all()
    matching = [r for r in all_saved if cuisine in r.cuisine]

    remaining = max(0, 10 - len(matching))
    if remaining == 0:
        return matching

    places = places_client.search_restaurants([cuisine], location, remaining).places

    results = list(matching)
    for restaurant in save_places(db, places, [cuisine]):
        if restaurant not in results:
            results.append(restaurant)
    return results


def save_places(db: Session, places: list[Place], fallback_cuisines: list[str]) -> list[Restaurant]:
    # Places can return restaurants we already saved (e.g. under another cuisine),
    # so only create rows for the ones we haven't seen
    place_ids = [p.id for p in places]
    saved_by_place_id = {
        r.place_id: r for r in db.scalars(select(Restaurant).where(Restaurant.place_id.in_(place_ids)))
    }
    new_restaurants = {
        place.id: _place_to_restaurant(place, fallback_cuisines)
        for place in places
        if place.id not in saved_by_place_id
    }
    db_helper.save_all(db, *new_restaurants.values())

    all_restaurants = saved_by_place_id | new_restaurants
    return [all_restaurants[place_id] for place_id in dict.fromkeys(place_ids)]


# Helpers

def _place_to_restaurant(place: Place, fallback_cuisines: list[str]) -> Restaurant:
    return Restaurant(
        place_id=place.id,
        cuisine=_extract_cuisines(place.types, fallback_cuisines),
        price_tier=_tier_to_number(place.price_level),
        place_long=place.location.longitude,
        place_lat=place.location.latitude,
        name=place.display_name.text
    )


def _extract_cuisines(types: list[str], fallback_cuisines: list[str]) -> list[str]:
    restaurant_types = [t for t in types if t.endswith("_restaurant")]
    if not restaurant_types:
        return fallback_cuisines
    else:
        return [rt.removesuffix("_restaurant") for rt in restaurant_types]


def _tier_to_number(tier: PriceLevel) -> int:
    # PRICE_LEVEL_UNSPECIFIED isn't in the list, so it becomes -1
    return PRICE_LEVELS_BY_TIER.index(tier) if tier in PRICE_LEVELS_BY_TIER else -1
