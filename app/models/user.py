from typing import Optional

from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    # Users who only sign in with Google have no password
    password_hash: Mapped[Optional[str]]
    google_sub: Mapped[Optional[str]] = mapped_column(unique=True)

    visits: Mapped[list["Visit"]] = relationship(back_populates="user")
    recommendations: Mapped[list["Recommendation"]] = relationship(back_populates="user")
