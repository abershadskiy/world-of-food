from app.dto.place import PlaceResults
from app.models.restaurant import Restaurant
from app.services import restaurant as restaurant_service


def make_places(*ids):
    return PlaceResults.model_validate({
        "places": [
            {
                "displayName": {"text": f"Place {i}"},
                "id": i,
                "location": {"latitude": 1.0, "longitude": 2.0},
                "types": ["thai_restaurant"],
            }
            for i in ids
        ]
    })


class FakePlacesClient:
    def __init__(self, results):
        self.results = results

    def search_restaurants(self, cuisine, city, page_size):
        return self.results


def test_search_twice_does_not_duplicate(db_session, monkeypatch):
    monkeypatch.setattr(restaurant_service, "places_client", FakePlacesClient(make_places("a", "b")))

    restaurant_service.get_restaurants(db_session, "thai", "Boston")
    results = restaurant_service.get_restaurants(db_session, "thai", "Boston")

    assert db_session.query(Restaurant).count() == 2
    assert len(results) == 2


def test_place_already_saved_under_other_cuisine_is_not_reinserted(db_session, monkeypatch):
    db_session.add(Restaurant(name="Place a", cuisine=["korean"], place_id="a", place_lat=1.0, place_long=2.0))
    db_session.commit()
    monkeypatch.setattr(restaurant_service, "places_client", FakePlacesClient(make_places("a", "b")))

    results = restaurant_service.get_restaurants(db_session, "thai", "Boston")

    assert db_session.query(Restaurant).count() == 2
    assert sorted(r.place_id for r in results) == ["a", "b"]
