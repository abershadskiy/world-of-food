from fastapi import Depends
from sqlalchemy.orm import Session

from app.clients.places import PlacesClient
from app.core.database import get_db
from app.models import User
from app.utils import db_helper

# Create clients
places_client = PlacesClient()


def get_user_or_404(user_id: int, db: Session = Depends(get_db)) -> User:
    return db_helper.get_or_404(db, User, user_id)