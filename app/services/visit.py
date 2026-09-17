from _pydatetime import date
from typing import Sequence

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dto.visit import VisitCreate
from app.models import Restaurant, Visit
from app.utils import db_helper


def create_visit(db: Session, user_id: int, visit_details: VisitCreate) -> Visit:
    db_helper.get_or_404(db, Restaurant, visit_details.restaurant_id)

    new_visit = Visit(
        user_id=user_id,
        restaurant_id=visit_details.restaurant_id,
        date=visit_details.date or date.today(),
        rating=visit_details.rating,
        notes=visit_details.notes
    )
    db_helper.save(db, new_visit)
    return new_visit

def get_visits(db: Session, user_id: int) -> Sequence[Visit]:
    return db.scalars(select(Visit).where(Visit.user_id == user_id)).all()
