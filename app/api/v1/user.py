from typing import Sequence

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_user_or_404
from app.dto.preference import UserPreferences
from app.dto.user import User
from app.dto.visit import VisitCreate, Visit
from app.models import User as UserModel
from app.services import user, visit, recommend

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post("/new", response_model=User)
def create_user(db: Session = Depends(get_db)):
    return user.add_user(db)


@router.post("/{user_id}/visits", response_model=Visit)
def create_visit(visit_details: VisitCreate, db_user: UserModel = Depends(get_user_or_404), db: Session = Depends(get_db)):
    return visit.create_visit(db, db_user.id, visit_details)

@router.get("/{user_id}/visits", response_model=Sequence[Visit])
def get_visits(db_user: UserModel = Depends(get_user_or_404), db: Session = Depends(get_db)):
    return visit.get_visits(db, db_user.id)

@router.get("/{user_id}/preferences", response_model=UserPreferences)
def get_preferences(db_user: UserModel = Depends(get_user_or_404), db: Session = Depends(get_db)):
    return recommend.get_user_preferences(db, db_user.id)