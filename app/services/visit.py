from typing import Sequence

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.dto.visit import VisitCreate, VisitUpdate
from app.models import Restaurant, Visit
from app.utils import db_helper


def create_visit(db: Session, user_id: int, visit_details: VisitCreate) -> Visit:
    db_helper.get_or_404(db, Restaurant, visit_details.restaurant_id)

    new_visit = Visit(
        user_id=user_id,
        restaurant_id=visit_details.restaurant_id,
        date=visit_details.date,
        rating=visit_details.rating,
        notes=visit_details.notes
    )
    db_helper.save(db, new_visit)
    return new_visit

def get_visits(db: Session, user_id: int) -> Sequence[Visit]:
    return db.scalars(select(Visit).where(Visit.user_id == user_id)).all()

def update_visit(db: Session, user_id: int, visit_id: int, changes: VisitUpdate) -> Visit:
    visit = _get_user_visit(db, user_id, visit_id)
    # Only the fields the client sent, so a missing field stays as it was
    for field, value in changes.model_dump(exclude_unset=True).items():
        setattr(visit, field, value)
    return db_helper.save(db, visit)

def delete_visit(db: Session, user_id: int, visit_id: int):
    visit = _get_user_visit(db, user_id, visit_id)
    db.delete(visit)
    db.commit()

def _get_user_visit(db: Session, user_id: int, visit_id: int) -> Visit:
    visit = db.scalars(select(Visit).where(Visit.id == visit_id, Visit.user_id == user_id)).first()
    if visit is None:
        raise HTTPException(status_code=404, detail=f"Visit {visit_id} not found")
    return visit
