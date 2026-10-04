from datetime import date

import pytest

from app.models import Restaurant, User, Visit
from app.services import recommend
from tests.factories import make_restaurant, make_visit


def add_visits(db, tiers):
    user = User()
    db.add(user)
    db.commit()
    for i, tier in enumerate(tiers):
        r = Restaurant(name=f"R{i}", cuisine=["thai"], price_tier=tier, place_id=str(i), place_lat=0.0, place_long=0.0)
        db.add(r)
        db.commit()
        db.add(Visit(user_id=user.id, restaurant_id=r.id, date=date.today()))
    db.commit()
    return user.id


class TestGetUserPreferences:
    def test_unspecified_prices_are_ignored(self, db_session):
        user_id = add_visits(db_session, [-1, -1, 2, 2, 3])
        prefs = recommend.get_user_preferences(db_session, user_id)
        assert prefs.price_tier == 2

    def test_median_is_an_int(self, db_session):
        user_id = add_visits(db_session, [1, 2, 2, 3, 3, 3])
        prefs = recommend.get_user_preferences(db_session, user_id)
        assert isinstance(prefs.price_tier, int)

    def test_all_prices_unspecified(self, db_session):
        user_id = add_visits(db_session, [-1] * 5)
        prefs = recommend.get_user_preferences(db_session, user_id)
        assert prefs.price_tier == -1


class TestRemoveVisited:
    @pytest.fixture
    def restaurants(self):
        return [make_restaurant(id=i) for i in range(1, 6)]

    def test_no_visits_removes_nothing(self, restaurants):
        assert recommend._remove_visited(restaurants, []) == restaurants

    def test_removes_visited_from_restaurants(self, restaurants):
        visit = make_visit(restaurant_id=restaurants[0].id)
        assert recommend._remove_visited(restaurants, [visit]) == restaurants[1:]
