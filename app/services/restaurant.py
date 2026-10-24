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
    matching = [r for r in all_saved if cuisine in r.cuisine and _in_location(r, location)]

    remaining = max(0, 10 - len(matching))
    if remaining == 0:
        return matching

    places = places_client.search_restaurants([cuisine], location, remaining).places

    results = list(matching)
    for restaurant in save_places(db, places):
        if restaurant not in results:
            results.append(restaurant)
    return results


def save_places(db: Session, places: list[Place]) -> list[Restaurant]:
    # Places can return restaurants we already saved (e.g. under another cuisine),
    # so only create rows for the ones we haven't seen
    place_ids = [p.id for p in places]
    saved_by_place_id = {
        r.place_id: r for r in db.scalars(select(Restaurant).where(Restaurant.place_id.in_(place_ids)))
    }
    new_restaurants = {
        place.id: _place_to_restaurant(place)
        for place in places
        if place.id not in saved_by_place_id
    }
    db_helper.save_all(db, *new_restaurants.values())

    all_restaurants = saved_by_place_id | new_restaurants
    return [all_restaurants[place_id] for place_id in dict.fromkeys(place_ids)]


# Helpers

def _place_to_restaurant(place: Place) -> Restaurant:
    return Restaurant(
        place_id=place.id,
        cuisine=_extract_cuisines(place.types),
        price_tier=_tier_to_number(place.price_level),
        place_long=place.location.longitude,
        place_lat=place.location.latitude,
        name=place.display_name.text,
        address=place.formatted_address,
        city=_address_part(place, "locality"),
        region=_address_part(place, "administrative_area_level_1"),
        country=_address_part(place, "country")
    )


def _extract_cuisines(types: list[str]) -> list[str]:
    # No cuisine type means we don't know it. Guessing from the search text saved names as cuisines.
    return [t.removesuffix("_restaurant") for t in types if t.endswith("_restaurant")]


def _address_part(place: Place, part_type: str) -> str | None:
    for component in place.address_components:
        if part_type in component.types:
            return component.long_text
    return None


def _in_location(restaurant: Restaurant, location: str) -> bool:
    # "Boston, MA" -> "boston". Matches a city, a state/region or a whole country.
    searched = location.split(",")[0].strip().lower()
    parts = [restaurant.city, restaurant.region, restaurant.country]
    return searched in [p.lower() for p in parts if p]


def _tier_to_number(tier: PriceLevel) -> int:
    # PRICE_LEVEL_UNSPECIFIED isn't in the list, so it becomes -1
    return PRICE_LEVELS_BY_TIER.index(tier) if tier in PRICE_LEVELS_BY_TIER else -1
