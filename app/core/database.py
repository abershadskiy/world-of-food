"""
SQLite + SQLAlchemy engine/session setup.

SQLite is used deliberately here (see project plan: "skip Postgres setup
overhead for a weekend"). If you outgrow this later, only this file needs
to change — swap SQLALCHEMY_DATABASE_URL for a Postgres URL.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./restaurant_tracker.db"

# check_same_thread=False is required for SQLite + FastAPI's threaded requests.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency: yields a DB session, always closes it after."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
