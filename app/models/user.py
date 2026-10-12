from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models import Visit


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)

    visits: Mapped[list[Visit]] = relationship(back_populates="user")
