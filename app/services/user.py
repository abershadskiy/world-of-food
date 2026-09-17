from sqlalchemy.orm import Session

from app.models import User, Visit
from app.utils import db_helper


def add_user(db: Session) -> User:
    user = User()
    db_helper.save(db, user)
    return user
