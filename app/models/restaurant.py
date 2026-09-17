"""
Data model — matches the plan:

  Restaurant: id, name, cuisine, price_tier, city, notes
  Visit:      id, restaurant_id, date, rating, notes
"""

from sqlalchemy import Column, Integer, String, Date, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship

from app.core.database import Base


class Restaurant(Base):
    __tablename__ = "restaurants"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, index=True)
    cuisine = Column(JSON, nullable=False, index=True)
    price_tier = Column(Integer, nullable=True)  # e.g. 1 ($) - 4 ($$$$)
    place_id = Column(String, nullable=False, unique=True)
    place_lat = Column(Float, nullable=False)
    place_long = Column(Float, nullable=False)

    visits = relationship(
        "Visit", back_populates="restaurant", cascade="all, delete-orphan"
    )
