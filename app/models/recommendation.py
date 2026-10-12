import enum
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import Integer, String, Column, Enum, TIMESTAMP

from app.core.database import Base

class Action(enum.Enum):
    LIKE = "like"
    MEH = "meh"
    REJECT = "reject"

class Recommendation(Base):
    __tablename__ = "recommendations"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(String, nullable=False, unique=True)
    action = Column(Enum, nullable=True)
    action_timestamp = Column(TIMESTAMP)

    visits = relationship(
        "Visit", back_populates="restaurant", cascade="all, delete-orphan"
    )
