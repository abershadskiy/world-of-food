import statistics
from typing import Counter

from sqlalchemy.orm import Session

from app.models.preference import UserPreferences
from app.services import visit as visit_service


def get_user_preferences(db: Session, user_id: int) -> UserPreferences:
    restaurant_visits = visit_service.get_visits(db, user_id)
    if len(restaurant_visits) < 5:
        return UserPreferences(
            top_cuisines=[],
            price_tier=-1,
            has_enough_data=False
        )
    else:
        found_cuisines = Counter()
        prices = []
        for visit in restaurant_visits:
            found_cuisines.update(visit.restaurant.cuisine)
            prices.append(visit.restaurant.price_tier)

        return UserPreferences(
            top_cuisines=[c for c, _ in found_cuisines.most_common(3)],
            price_tier=statistics.median(prices),
            has_enough_data=True
        )




