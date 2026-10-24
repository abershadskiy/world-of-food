import jwt
from datetime import datetime, timedelta, timezone

from app.core.config import settings
from tests.api.conftest import auth_header, google_identity, signup


class TestSignupAndLogin:
    def test_signup_token_identifies_the_new_user(self, client):
        token = signup(client, "a@example.com")

        me = client.get("/v1/auth/me", headers=auth_header(token))

        assert me.status_code == 200
        assert me.json()["email"] == "a@example.com"

    def test_signup_with_taken_email_is_rejected_regardless_of_case(self, client):
        signup(client, "a@example.com")

        response = client.post("/v1/auth/signup", json={"email": "A@Example.com", "password": "password123"})

        assert response.status_code == 409

    def test_short_password_is_rejected(self, client):
        response = client.post("/v1/auth/signup", json={"email": "a@example.com", "password": "short"})

        assert response.status_code == 422

    def test_login_with_right_password(self, client):
        signup(client, "a@example.com", "password123")

        response = client.post("/v1/auth/login", json={"email": "a@example.com", "password": "password123"})

        assert response.status_code == 200
        assert response.json()["access_token"]

    def test_wrong_password_and_unknown_email_look_the_same(self, client):
        signup(client, "a@example.com", "password123")

        wrong_password = client.post("/v1/auth/login", json={"email": "a@example.com", "password": "nope-nope"})
        unknown_email = client.post("/v1/auth/login", json={"email": "who@example.com", "password": "password123"})

        assert wrong_password.status_code == unknown_email.status_code == 401
        assert wrong_password.json() == unknown_email.json()


class TestProtectedRoutes:
    def test_no_token_is_401(self, client):
        assert client.get("/v1/users/1/visits").status_code == 401
        assert client.get("/v1/restaurants/", params={"cuisine": "thai", "location": "x"}).status_code == 401

    def test_garbage_token_is_401(self, client):
        assert client.get("/v1/auth/me", headers=auth_header("not-a-token")).status_code == 401

    def test_expired_token_is_401(self, client):
        user_id = client.get("/v1/auth/me", headers=auth_header(signup(client))).json()["id"]
        expired = jwt.encode(
            {"sub": str(user_id), "exp": datetime.now(timezone.utc) - timedelta(minutes=1)},
            settings.SECRET_KEY, algorithm="HS256"
        )

        assert client.get("/v1/auth/me", headers=auth_header(expired)).status_code == 401

    def test_user_can_read_own_data(self, client):
        token = signup(client)
        user_id = client.get("/v1/auth/me", headers=auth_header(token)).json()["id"]

        response = client.get(f"/v1/users/{user_id}/visits", headers=auth_header(token))

        assert response.status_code == 200
        assert response.json() == []

    def test_user_cannot_read_someone_elses_data(self, client):
        first_token = signup(client, "a@example.com")
        first_id = client.get("/v1/auth/me", headers=auth_header(first_token)).json()["id"]
        second_token = signup(client, "b@example.com")

        response = client.get(f"/v1/users/{first_id}/visits", headers=auth_header(second_token))

        assert response.status_code == 404


class TestGoogleLogin:
    def test_new_google_user_is_created(self, client, google):
        google.identity = google_identity(email="g@example.com")

        response = client.post("/v1/auth/google", json={"id_token": "t"})

        me = client.get("/v1/auth/me", headers=auth_header(response.json()["access_token"]))
        assert me.json()["email"] == "g@example.com"

    def test_signing_in_twice_gives_the_same_user(self, client, google):
        google.identity = google_identity()

        first = client.post("/v1/auth/google", json={"id_token": "t"}).json()["access_token"]
        second = client.post("/v1/auth/google", json={"id_token": "t"}).json()["access_token"]

        ids = [client.get("/v1/auth/me", headers=auth_header(t)).json()["id"] for t in (first, second)]
        assert ids[0] == ids[1]

    def test_links_to_existing_password_account_with_same_email(self, client, google):
        password_token = signup(client, "g@example.com")
        google.identity = google_identity(email="g@example.com")

        google_token = client.post("/v1/auth/google", json={"id_token": "t"}).json()["access_token"]

        ids = [client.get("/v1/auth/me", headers=auth_header(t)).json()["id"] for t in (password_token, google_token)]
        assert ids[0] == ids[1]

    def test_unverified_google_email_is_rejected(self, client, google):
        google.identity = google_identity(verified=False)

        assert client.post("/v1/auth/google", json={"id_token": "t"}).status_code == 401

    def test_invalid_google_token_is_rejected(self, client, google):
        google.identity = None

        assert client.post("/v1/auth/google", json={"id_token": "t"}).status_code == 401

    def test_google_only_user_cannot_log_in_with_a_password(self, client, google):
        google.identity = google_identity(email="g@example.com")
        client.post("/v1/auth/google", json={"id_token": "t"})

        response = client.post("/v1/auth/login", json={"email": "g@example.com", "password": "password123"})

        assert response.status_code == 401

    def test_google_login_is_off_without_a_client_id(self, client, google, monkeypatch):
        monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", None)

        assert client.post("/v1/auth/google", json={"id_token": "t"}).status_code == 503


def test_root_redirects_to_ui(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "http://localhost:5173"
