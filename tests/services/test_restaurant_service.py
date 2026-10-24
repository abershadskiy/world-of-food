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


def save_restaurant(db_session, place_id, city, country):
    db_session.add(Restaurant(name=place_id, cuisine=["thai"], place_id=place_id, place_lat=1.0, place_long=2.0,
                              city=city, country=country))
    db_session.commit()


def test_saved_results_are_filtered_by_location(db_session, monkeypatch):
    save_restaurant(db_session, "boston", "Boston", "United States")
    save_restaurant(db_session, "tokyo", "Tokyo", "Japan")
    monkeypatch.setattr(restaurant_service, "places_client", FakePlacesClient(PlaceResults()))

    assert [r.place_id for r in restaurant_service.get_restaurants(db_session, "thai", "boston, MA")] == ["boston"]
    assert [r.place_id for r in restaurant_service.get_restaurants(db_session, "thai", "Japan")] == ["tokyo"]


def test_saves_address_from_places(db_session, monkeypatch):
    results = PlaceResults.model_validate({"places": [{
        "displayName": {"text": "Two Schmucks"},
        "id": "ts",
        "location": {"latitude": 41.4, "longitude": 2.2},
        "types": ["bar"],
        "formattedAddress": "Carrer de Joaquín Costa, 52, 08001 Barcelona, Spain",
        "addressComponents": [
            {"longText": "Barcelona", "types": ["locality", "political"]},
            {"longText": "Catalonia", "types": ["administrative_area_level_1", "political"]},
            {"longText": "Spain", "types": ["country", "political"]},
        ],
    }]})
    monkeypatch.setattr(restaurant_service, "places_client", FakePlacesClient(results))

    saved = restaurant_service.get_restaurants(db_session, "two schmucks", "Barcelona")[0]

    assert (saved.city, saved.region, saved.country) == ("Barcelona", "Catalonia", "Spain")
    assert saved.address == "Carrer de Joaquín Costa, 52, 08001 Barcelona, Spain"
    # No *_restaurant type, so the cuisine is unknown rather than the search text
    assert saved.cuisine == []
