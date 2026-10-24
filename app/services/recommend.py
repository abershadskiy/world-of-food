import statistics
from collections import Counter
from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.dependencies import places_client
from app.models import Recommendation, Restaurant, Visit
from app.models.preference import UserPreferences
from app.models.recommendation import Action
from app.services import restaurant as restaurant_service, visit as visit_service
from app.utils import db_helper

RECOMMENDATION_COUNT = 10


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
            if visit.restaurant.price_tier >= 0:
                prices.append(visit.restaurant.price_tier)

        return UserPreferences(
            top_cuisines=[c for c, _ in found_cuisines.most_common(3)],
            price_tier=round(statistics.median(prices)) if prices else -1,
            has_enough_data=True
        )

def get_recommendations(db: Session, user_id: int, action: Action | None = None) -> list[Recommendation]:
    """Recommendations with the given action (pending ones when None) that the user hasn't visited. Doesn't call Places."""
    visited_ids = {v.restaurant_id for v in visit_service.get_visits(db, user_id)}
    if action is None:
        action_filter = Recommendation.action.is_(None)
    else:
        action_filter = Recommendation.action == action
    recommendations = db.scalars(
        select(Recommendation)
        .where(Recommendation.user_id == user_id, action_filter)
        .order_by(Recommendation.id)
    ).all()
    return [r for r in recommendations if r.restaurant_id not in visited_ids]


def refresh_recommendations(db: Session, user_id: int, location: str) -> list[Recommendation]:
    """Searches Places for new restaurants, saves them as recommendations, returns the pending ones from this search."""
    preferences = get_user_preferences(db, user_id)
    visits = visit_service.get_visits(db, user_id)

    already_recommended = set(
        db.scalars(select(Recommendation.restaurant_id).where(Recommendation.user_id == user_id))
    )
    candidates = _remove_visited(_find_candidates(db, preferences, location), visits)
    new = [
        Recommendation(user_id=user_id, restaurant_id=r.id)
        for r in candidates
        if r.id not in already_recommended
    ]
    db_helper.save_all(db, *new)

    candidate_ids = [r.id for r in candidates]
    return list(db.scalars(
        select(Recommendation)
        .where(
            Recommendation.user_id == user_id,
            Recommendation.restaurant_id.in_(candidate_ids),
            Recommendation.action.is_(None)
        )
        .order_by(Recommendation.id)
    ).all())


def set_recommendation_action(db: Session, user_id: int, recommendation_id: int, action: Action | None) -> Recommendation:
    """Sets the action, or clears it when None so the recommendation is pending again."""
    recommendation = db.scalars(
        select(Recommendation).where(Recommendation.id == recommendation_id, Recommendation.user_id == user_id)
    ).first()
    if recommendation is None:
        raise HTTPException(status_code=404, detail=f"Recommendation {recommendation_id} not found")

    recommendation.action = action
    recommendation.action_timestamp = datetime.now() if action is not None else None
    db.commit()
    db.refresh(recommendation)
    return recommendation


def _find_candidates(db: Session, preferences: UserPreferences, location: str) -> list[Restaurant]:
    if preferences.has_enough_data:
        places = places_client.search_restaurants(
            preferences.top_cuisines, location, RECOMMENDATION_COUNT, preferences.price_tier
        ).places
    else:
        places = places_client.search_default_restaurants(location, RECOMMENDATION_COUNT).places
    # We don't know which cuisine a place matched, so an unlabeled place gets no cuisine
    return restaurant_service.save_places(db, places)


def _remove_visited(restaurants: list[Restaurant], visits: list[Visit]) -> list[Restaurant]:
    visited_ids = {v.restaurant_id for v in visits}
    return list(filter(lambda r: r.id not in visited_ids, restaurants))


