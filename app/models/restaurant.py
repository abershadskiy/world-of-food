from typing import Optional

from sqlalchemy import JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class Restaurant(Base):
    __tablename__ = "restaurants"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(index=True)
    cuisine: Mapped[list[str]] = mapped_column(JSON)
    price_tier: Mapped[int] = mapped_column(default=-1)  # -1 unknown, 0 free, 1 ($) - 4 ($$$$)
    place_id: Mapped[str] = mapped_column(unique=True)
    place_lat: Mapped[float]
    place_long: Mapped[float]
    address: Mapped[Optional[str]]
    city: Mapped[Optional[str]]
    region: Mapped[Optional[str]]  # state or province
    country: Mapped[Optional[str]]

    visits: Mapped[list["Visit"]] = relationship(
        back_populates="restaurant", cascade="all, delete-orphan"
    )
    recommendations: Mapped[list["Recommendation"]] = relationship(
        back_populates="restaurant", cascade="all, delete-orphan"
    )
