import datetime
import enum
from typing import Optional

from sqlalchemy import UniqueConstraint, ForeignKey
from sqlalchemy.orm import relationship, Mapped, mapped_column

from app.core.database import Base
from app.models.restaurant import Restaurant
from app.models.user import User


class Action(enum.Enum):
    LIKE = "like"
    MEH = "meh"
    REJECT = "reject"


class Recommendation(Base):
    __tablename__ = "recommendations"
    __table_args__ = (UniqueConstraint("user_id", "restaurant_id"),)

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    restaurant_id: Mapped[int] = mapped_column(ForeignKey("restaurants.id"))
    action: Mapped[Optional[Action]]
    action_timestamp: Mapped[Optional[datetime.datetime]]

    user: Mapped[User] = relationship(back_populates="recommendations")
    restaurant: Mapped[Restaurant] = relationship(back_populates="recommendations")
