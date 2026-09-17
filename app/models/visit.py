from sqlalchemy import Column, Integer, Date, String, ForeignKey
from sqlalchemy.orm import relationship, Mapped

from app.core.database import Base
from app.models import Restaurant


class Visit(Base):
    __tablename__ = "visits"

    id = Column(Integer, primary_key=True, index=True)
    restaurant_id = Column(Integer, ForeignKey("restaurants.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    date = Column(Date, nullable=False, index=True)
    rating = Column(Integer, nullable=True)
    notes = Column(String, nullable=True)

    restaurant: Mapped[Restaurant] = relationship("Restaurant", back_populates="visits", lazy="joined")
    user = relationship("User", back_populates="visits")
