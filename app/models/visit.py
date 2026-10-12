import datetime
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.restaurant import Restaurant
from app.models.user import User


class Visit(Base):
    __tablename__ = "visits"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"))
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    date: Mapped[datetime.date] = mapped_column(index=True)
    rating: Mapped[Optional[int]]
    notes: Mapped[Optional[str]]

    restaurant: Mapped[Restaurant] = relationship(back_populates="visits", lazy="joined")
    user: Mapped[User] = relationship(back_populates="visits")
