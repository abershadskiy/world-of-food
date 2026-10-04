import httpx
import pytest

from app.clients.places import PlacesClient


def test_bad_response_raises_clear_error(monkeypatch):
    request = httpx.Request("POST", "https://places.googleapis.com/v1/places:searchText")
    monkeypatch.setattr(httpx, "post", lambda *a, **kw: httpx.Response(403, json={"error": "bad key"}, request=request))

    with pytest.raises(httpx.HTTPStatusError):
        PlacesClient().search_restaurants("thai", "Boston", 5)
