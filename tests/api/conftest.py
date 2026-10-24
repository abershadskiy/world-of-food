import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models
from app.clients.google_auth import GoogleIdentity
from app.core.config import settings
from app.core.database import Base, get_db
from app.main import app as fastapi_app
from app.services import auth


class FakeGoogleClient:
    def __init__(self):
        self.identity = None

    def verify(self, token):
        return self.identity


@pytest.fixture
def client():
    # TestClient runs requests on another thread, so every thread has to share one in-memory DB
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    def override_get_db():
        db = Session()
        try:
            yield db
        finally:
            db.close()

    fastapi_app.dependency_overrides[get_db] = override_get_db
    yield TestClient(fastapi_app)
    fastapi_app.dependency_overrides.clear()


@pytest.fixture
def google(monkeypatch):
    fake = FakeGoogleClient()
    monkeypatch.setattr(auth, "google_client", fake)
    monkeypatch.setattr(settings, "GOOGLE_CLIENT_ID", "test-client-id")
    return fake


def google_identity(sub="g-1", email="g@example.com", verified=True):
    return GoogleIdentity(sub=sub, email=email, email_verified=verified)


def signup(client, email="a@example.com", password="password123"):
    response = client.post("/v1/auth/signup", json={"email": email, "password": password})
    return response.json()["access_token"]


def auth_header(token):
    return {"Authorization": f"Bearer {token}"}
