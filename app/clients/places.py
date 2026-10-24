from typing import Optional

import httpx

from app.core.config import settings
from app.dto.place import PlaceResults, PRICE_LEVELS_BY_TIER


class PlacesClient:
    def __init__(self):
        self.api_key = settings.PLACES_API_KEY
        self.base_url = "https://places.googleapis.com/v1/places:searchText"

    def search_restaurants(self, cuisines: list[str], location: Optional[str], page_size: int,
                           price_tier: int = -1) -> PlaceResults:
        text_query = " or ".join(cuisines)
        if location:
            text_query += f" near {location}"
        return self._search(text_query, page_size, _price_levels_near(price_tier))

    def search_default_restaurants(self, location: Optional[str], page_size: int) -> PlaceResults:
        text_query = f"restaurants near {location}" if location else "restaurants"
        return self._search(text_query, page_size, [])

    def _search(self, text_query: str, page_size: int, price_levels: list[str]) -> PlaceResults:
        headers = {
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.displayName,places.id,places.priceLevel,places.location,places.types,"
                                "places.formattedAddress,places.addressComponents"
        }
        # No includedType: it only takes one type, and bars, cafes and bakeries count too
        request_content = {
            "textQuery": text_query,
            "pageSize": page_size
        }
        if price_levels:
            request_content["priceLevels"] = price_levels
        response = httpx.post(self.base_url, headers=headers, json=request_content, timeout=10)
        response.raise_for_status()

        results = PlaceResults.model_validate(response.json())
        results.places = [p for p in results.places if _serves_food(p.types)]
        return results


FOOD_TYPES = {"restaurant", "food", "cafe", "coffee_shop", "bar", "pub", "bakery", "meal_takeaway", "meal_delivery",
              "food_court"}

def _serves_food(types: list[str]) -> bool:
    return any(t in FOOD_TYPES or t.endswith("_restaurant") for t in types)


def _price_levels_near(price_tier: int) -> list[str]:
    # Include the tiers on either side so a narrow filter doesn't return almost nothing.
    # -1 means we don't know the user's price range, so no filter.
    if price_tier < 0:
        return []
    low = max(0, price_tier - 1)
    high = min(len(PRICE_LEVELS_BY_TIER) - 1, price_tier + 1)
    return [level.value for level in PRICE_LEVELS_BY_TIER[low:high + 1]]
