from typing import Sequence

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_user_or_404
from app.dto.preference import UserPreferences
from app.dto.recommendation import Recommendation, RecommendationAction
from app.dto.visit import VisitCreate, VisitUpdate, Visit
from app.models import User as UserModel
from app.models.recommendation import Action
from app.services import visit, recommend

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.post("/{user_id}/visits", response_model=Visit)
def create_visit(visit_details: VisitCreate, db_user: UserModel = Depends(get_user_or_404), db: Session = Depends(get_db)):
    return visit.create_visit(db, db_user.id, visit_details)

@router.get("/{user_id}/visits", response_model=Sequence[Visit])
def get_visits(db_user: UserModel = Depends(get_user_or_404), db: Session = Depends(get_db)):
    return visit.get_visits(db, db_user.id)

@router.patch("/{user_id}/visits/{visit_id}", response_model=Visit)
def update_visit(visit_id: int, changes: VisitUpdate, db_user: UserModel = Depends(get_user_or_404), db: Session = Depends(get_db)):
    return visit.update_visit(db, db_user.id, visit_id, changes)

@router.delete("/{user_id}/visits/{visit_id}", status_code=204)
def delete_visit(visit_id: int, db_user: UserModel = Depends(get_user_or_404), db: Session = Depends(get_db)):
    visit.delete_visit(db, db_user.id, visit_id)

@router.get("/{user_id}/preferences", response_model=UserPreferences)
def get_preferences(db_user: UserModel = Depends(get_user_or_404), db: Session = Depends(get_db)):
    return recommend.get_user_preferences(db, db_user.id)

@router.get("/{user_id}/recommendations", response_model=Sequence[Recommendation])
def get_recommendations(action: Action | None = None, db_user: UserModel = Depends(get_user_or_404), db: Session = Depends(get_db)):
    return recommend.get_recommendations(db, db_user.id, action)

@router.post("/{user_id}/recommendations/refresh", response_model=Sequence[Recommendation])
def refresh_recommendations(location: str, db_user: UserModel = Depends(get_user_or_404), db: Session = Depends(get_db)):
    return recommend.refresh_recommendations(db, db_user.id, location)

@router.patch("/{user_id}/recommendations/{recommendation_id}", response_model=Recommendation)
def set_recommendation_action(recommendation_id: int, body: RecommendationAction, db_user: UserModel = Depends(get_user_or_404), db: Session = Depends(get_db)):
    return recommend.set_recommendation_action(db, db_user.id, recommendation_id, body.action)
