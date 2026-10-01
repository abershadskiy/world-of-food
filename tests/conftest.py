import os

# Settings needs a key at import time; tests never call the real API
os.environ.setdefault("PLACES_API_KEY", "test-key")

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytest
import app.models

from app.core.database import Base, get_db

engine = create_engine("sqlite:///:memory:", echo=True)
TestSessionLocal = sessionmaker(bind=engine)

@pytest.fixture(scope='function')
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def db_session(setup_db):
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()
