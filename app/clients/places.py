from typing import Optional

import httpx

from app.core.config import settings
from app.dto.place import PlaceResults


class PlacesClient:
    def __init__(self):
        self.api_key = settings.PLACES_API_KEY
        self.base_url = "https://places.googleapis.com/v1/places:searchText"

    def search_restaurants(self, cuisine: str, city: Optional[str], page_size: int) -> PlaceResults:
        text_query = f"{cuisine} {city}" if city else cuisine
        headers = {
            "X-Goog-Api-Key": self.api_key,
            "X-Goog-FieldMask": "places.displayName,places.id,places.priceLevel,places.location,places.types"
        }
        request_content = {
            "textQuery": text_query,
            "pageSize": page_size,
            "includedType": "restaurant"
        }
        response = httpx.post(self.base_url, headers=headers, json=request_content, timeout=10)
        response.raise_for_status()

        return PlaceResults.model_validate(response.json())
