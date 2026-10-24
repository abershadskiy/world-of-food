import pytest

from app.services import recommend
from tests.api.conftest import auth_header, signup
from tests.services.test_recommend_service import FakePlacesClient, make_place


@pytest.fixture
def user(client, monkeypatch):
    monkeypatch.setattr(recommend, "places_client", FakePlacesClient([make_place("a"), make_place("b")]))
    headers = auth_header(signup(client))
    user_id = client.get("/v1/auth/me", headers=headers).json()["id"]
    return f"/v1/users/{user_id}", headers


def refresh(client, user):
    url, headers = user
    return client.post(f"{url}/recommendations/refresh?location=Boston", headers=headers).json()


class TestRecommendationsApi:
    def test_lists_by_action_and_undoes(self, client, user):
        url, headers = user
        rec = refresh(client, user)[0]

        liked = client.patch(f"{url}/recommendations/{rec['id']}", json={"action": "like"}, headers=headers)
        assert liked.json()["action"] == "like"
        assert [r["id"] for r in client.get(f"{url}/recommendations?action=like", headers=headers).json()] == [rec["id"]]

        undone = client.patch(f"{url}/recommendations/{rec['id']}", json={"action": None}, headers=headers)
        assert undone.json()["action"] is None
        assert client.get(f"{url}/recommendations?action=like", headers=headers).json() == []

    def test_action_must_be_sent(self, client, user):
        url, headers = user
        rec = refresh(client, user)[0]

        response = client.patch(f"{url}/recommendations/{rec['id']}", json={}, headers=headers)

        assert response.status_code == 422


class TestVisitsApi:
    @pytest.fixture
    def visit(self, client, user):
        url, headers = user
        restaurant_id = refresh(client, user)[0]["restaurant"]["id"]
        body = {"restaurant_id": restaurant_id, "date": "2026-01-01", "rating": 3, "notes": "ok"}
        return client.post(f"{url}/visits", json=body, headers=headers).json()

    def test_edit_visit(self, client, user, visit):
        url, headers = user

        response = client.patch(f"{url}/visits/{visit['id']}", json={"rating": 5}, headers=headers)

        assert response.status_code == 200
        assert response.json()["rating"] == 5
        assert response.json()["notes"] == "ok"

    def test_date_cannot_be_cleared(self, client, user, visit):
        url, headers = user

        response = client.patch(f"{url}/visits/{visit['id']}", json={"date": None}, headers=headers)

        assert response.status_code == 422

    def test_delete_visit(self, client, user, visit):
        url, headers = user

        response = client.delete(f"{url}/visits/{visit['id']}", headers=headers)

        assert response.status_code == 204
        assert client.get(f"{url}/visits", headers=headers).json() == []

    def test_missing_visit_is_404(self, client, user):
        url, headers = user

        assert client.delete(f"{url}/visits/999", headers=headers).status_code == 404
        assert client.patch(f"{url}/visits/999", json={"rating": 1}, headers=headers).status_code == 404
