from datetime import date

import pytest
from fastapi import HTTPException

from app.dto.place import Place, PlaceResults
from app.models import Restaurant, User, Visit
from app.models.recommendation import Action
from app.services import recommend
from tests.factories import make_restaurant, make_user, make_visit


def add_visits(db, tiers):
    user = make_user()
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

    def test_returns_no_restaurants_if_all_visited(self, restaurants):
        visits = [make_visit(restaurant_id=r.id) for r in restaurants]
        assert recommend._remove_visited(restaurants, visits) == []

    def test_returns_restaurants_unfiltered_if_visits_unrelated(self, restaurants):
        unrelated_visit = make_visit(restaurant_id=999)
        assert recommend._remove_visited(restaurants, [unrelated_visit]) == restaurants


class FakePlacesClient:
    def __init__(self, places=()):
        self.places = places
        self.calls = []

    def search_restaurants(self, cuisines, location, page_size, price_tier=-1):
        self.calls.append(("preferences", cuisines, location, price_tier))
        return PlaceResults(places=self.places)

    def search_default_restaurants(self, location, page_size):
        self.calls.append(("default", location))
        return PlaceResults(places=self.places)


def make_place(place_id):
    return Place.model_validate({
        "displayName": {"text": f"Place {place_id}"},
        "id": place_id,
        "location": {"latitude": 1.0, "longitude": 2.0},
        "types": ["thai_restaurant"],
    })


@pytest.fixture
def user_id(db_session):
    user = make_user()
    db_session.add(user)
    db_session.commit()
    return user.id


@pytest.fixture
def places_client(monkeypatch):
    client = FakePlacesClient([make_place("a"), make_place("b"), make_place("c")])
    monkeypatch.setattr(recommend, "places_client", client)
    return client


class TestRefreshRecommendations:
    def test_returns_new_recommendations(self, db_session, user_id, places_client):
        recs = recommend.refresh_recommendations(db_session, user_id, "Boston")

        assert len(recs) == 3

    def test_refreshing_twice_does_not_duplicate(self, db_session, user_id, places_client):
        recommend.refresh_recommendations(db_session, user_id, "Boston")
        recs = recommend.refresh_recommendations(db_session, user_id, "Boston")

        assert len(recs) == 3

    def test_acted_on_recommendation_is_not_recommended_again(self, db_session, user_id, places_client):
        first = recommend.refresh_recommendations(db_session, user_id, "Boston")[0]
        recommend.set_recommendation_action(db_session, user_id, first.id, Action.REJECT)

        recs = recommend.refresh_recommendations(db_session, user_id, "Boston")

        assert first.restaurant_id not in {r.restaurant_id for r in recs}
        assert len(recs) == 2

    def test_visited_restaurant_is_not_recommended(self, db_session, user_id, places_client):
        first = recommend.refresh_recommendations(db_session, user_id, "Boston")[0]
        db_session.add(Visit(user_id=user_id, restaurant_id=first.restaurant_id, date=date.today()))
        db_session.commit()

        recs = recommend.refresh_recommendations(db_session, user_id, "Boston")

        assert first.restaurant_id not in {r.restaurant_id for r in recs}

    def test_without_enough_visits_uses_default_search(self, db_session, user_id, places_client):
        recommend.refresh_recommendations(db_session, user_id, "Boston")

        assert places_client.calls == [("default", "Boston")]

    def test_only_returns_this_searchs_recommendations(self, db_session, user_id, places_client):
        recommend.refresh_recommendations(db_session, user_id, "Tokyo")
        places_client.places = [make_place("d"), make_place("e")]

        recs = recommend.refresh_recommendations(db_session, user_id, "Boston")

        assert {r.restaurant.place_id for r in recs} == {"d", "e"}

    def test_repeat_search_returns_its_earlier_pending_recommendations(self, db_session, user_id, places_client):
        first = recommend.refresh_recommendations(db_session, user_id, "Boston")
        places_client.places = [make_place("a"), make_place("d")]

        recs = recommend.refresh_recommendations(db_session, user_id, "Boston")

        assert {r.restaurant.place_id for r in recs} == {"a", "d"}
        assert recs[0] == first[0]

    def test_with_enough_visits_searches_by_preferences(self, db_session, places_client):
        user_id = add_visits(db_session, [2, 2, 2, 2, 2])

        recommend.refresh_recommendations(db_session, user_id, "Boston")

        assert places_client.calls == [("preferences", ["thai"], "Boston", 2)]


class TestGetRecommendations:
    def test_does_not_call_places(self, db_session, user_id, places_client):
        recommend.get_recommendations(db_session, user_id)

        assert places_client.calls == []

    def test_only_returns_recommendations_without_an_action(self, db_session, user_id, places_client):
        recs = recommend.refresh_recommendations(db_session, user_id, "Boston")
        recommend.set_recommendation_action(db_session, user_id, recs[0].id, Action.LIKE)

        assert recommend.get_recommendations(db_session, user_id) == recs[1:]

    def test_visited_since_recommended_is_dropped(self, db_session, user_id, places_client):
        first = recommend.refresh_recommendations(db_session, user_id, "Boston")[0]
        db_session.add(Visit(user_id=user_id, restaurant_id=first.restaurant_id, date=date.today()))
        db_session.commit()

        recs = recommend.get_recommendations(db_session, user_id)

        assert first not in recs
        assert len(recs) == 2

    def test_filters_by_action(self, db_session, user_id, places_client):
        recs = recommend.refresh_recommendations(db_session, user_id, "Boston")
        recommend.set_recommendation_action(db_session, user_id, recs[0].id, Action.LIKE)
        recommend.set_recommendation_action(db_session, user_id, recs[1].id, Action.REJECT)

        assert recommend.get_recommendations(db_session, user_id, Action.LIKE) == [recs[0]]
        assert recommend.get_recommendations(db_session, user_id, Action.REJECT) == [recs[1]]
        assert recommend.get_recommendations(db_session, user_id, Action.MEH) == []


class TestSetRecommendationAction:
    def test_sets_action_and_timestamp(self, db_session, user_id, places_client):
        rec = recommend.refresh_recommendations(db_session, user_id, "Boston")[0]

        updated = recommend.set_recommendation_action(db_session, user_id, rec.id, Action.MEH)

        assert updated.action == Action.MEH
        assert updated.action_timestamp is not None

    def test_none_undoes_the_action(self, db_session, user_id, places_client):
        rec = recommend.refresh_recommendations(db_session, user_id, "Boston")[0]
        recommend.set_recommendation_action(db_session, user_id, rec.id, Action.LIKE)

        undone = recommend.set_recommendation_action(db_session, user_id, rec.id, None)

        assert undone.action is None
        assert undone.action_timestamp is None
        assert rec in recommend.get_recommendations(db_session, user_id)

    def test_other_users_recommendation_is_404(self, db_session, user_id, places_client):
        rec = recommend.refresh_recommendations(db_session, user_id, "Boston")[0]

        with pytest.raises(HTTPException) as error:
            recommend.set_recommendation_action(db_session, user_id + 1, rec.id, Action.LIKE)

        assert error.value.status_code == 404
