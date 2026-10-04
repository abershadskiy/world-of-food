import datetime
import itertools

from app.models import Restaurant, Visit

_ids = itertools.count(1)


def make_restaurant(**overrides) -> Restaurant:
    fields = {
        "name": "Test Place",
        "cuisine": ["italian"],
        "price_tier": 2,
        "place_id": f"place--{next(_ids)}",
        "place_lat": 0.0,
        "place_long": 0.0
    }
    fields.update(overrides)
    return Restaurant(**fields)


def make_visit(**overrides) -> Visit:
    fields = {
        "restaurant_id": f"restaurant--{next(_ids)}",
        "user_id": f"user--{next(_ids)}",
        "date": datetime.date.today(),
        "rating": 5,
        "notes": "loved it"
    }
    fields.update(overrides)
    return Visit(**fields)