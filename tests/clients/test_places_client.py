import httpx
import pytest

from app.clients.places import PlacesClient


def test_bad_response_raises_clear_error(monkeypatch):
    request = httpx.Request("POST", "https://places.googleapis.com/v1/places:searchText")
    monkeypatch.setattr(httpx, "post", lambda *a, **kw: httpx.Response(403, json={"error": "bad key"}, request=request))

    with pytest.raises(httpx.HTTPStatusError):
        PlacesClient().search_restaurants(["thai"], "Boston", 5)


def sent_body(monkeypatch):
    sent = {}
    request = httpx.Request("POST", "https://places.googleapis.com/v1/places:searchText")

    def fake_post(url, headers, json, timeout):
        sent.update(json)
        return httpx.Response(200, json={"places": []}, request=request)

    monkeypatch.setattr(httpx, "post", fake_post)
    return sent


def test_multiple_cuisines_become_an_or_query(monkeypatch):
    sent = sent_body(monkeypatch)
    PlacesClient().search_restaurants(["thai", "italian"], "Boston", 5)
    assert sent["textQuery"] == "thai or italian near Boston"


def test_price_tier_filters_to_neighboring_tiers(monkeypatch):
    sent = sent_body(monkeypatch)
    PlacesClient().search_restaurants(["thai"], "Boston", 5, price_tier=2)
    assert sent["priceLevels"] == ["PRICE_LEVEL_INEXPENSIVE", "PRICE_LEVEL_MODERATE", "PRICE_LEVEL_EXPENSIVE"]


def test_unknown_price_tier_sends_no_filter(monkeypatch):
    sent = sent_body(monkeypatch)
    PlacesClient().search_restaurants(["thai"], "Boston", 5, price_tier=-1)
    assert "priceLevels" not in sent


def test_default_search_has_no_price_filter(monkeypatch):
    sent = sent_body(monkeypatch)
    PlacesClient().search_default_restaurants("Boston", 5)
    assert sent["textQuery"] == "restaurants near Boston"
    assert "priceLevels" not in sent


def respond_with(monkeypatch, body):
    request = httpx.Request("POST", "https://places.googleapis.com/v1/places:searchText")
    monkeypatch.setattr(httpx, "post", lambda *a, **kw: httpx.Response(200, json=body, request=request))


def place(place_id, types):
    return {"displayName": {"text": place_id}, "id": place_id, "location": {"latitude": 1.0, "longitude": 2.0},
            "types": types}


def test_no_matches_is_an_empty_list(monkeypatch):
    # Places sends {} rather than {"places": []}
    respond_with(monkeypatch, {})
    assert PlacesClient().search_restaurants(["thai"], "Barcelona", 5).places == []


def test_keeps_any_place_that_serves_food(monkeypatch):
    respond_with(monkeypatch, {"places": [
        place("bar", ["bar", "point_of_interest"]),
        place("cafe", ["cafe", "food"]),
        place("thai", ["thai_restaurant"]),
        place("gym", ["gym", "point_of_interest"]),
    ]})

    results = PlacesClient().search_restaurants(["two schmucks"], "Barcelona", 5)

    assert [p.id for p in results.places] == ["bar", "cafe", "thai"]


def test_search_is_not_limited_to_restaurants(monkeypatch):
    sent = sent_body(monkeypatch)
    PlacesClient().search_restaurants(["thai"], "Boston", 5)
    assert "includedType" not in sent
