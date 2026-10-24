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
