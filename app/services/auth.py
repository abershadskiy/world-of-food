from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.clients.google_auth import GoogleAuthClient
from app.core import security
from app.core.config import settings
from app.models import User
from app.utils import db_helper

google_client = GoogleAuthClient()


def signup(db: Session, email: str, password: str) -> str:
    email = email.lower()
    if _find_by_email(db, email):
        raise HTTPException(status_code=409, detail="That email is already registered")

    user = db_helper.save(db, User(email=email, password_hash=security.hash_password(password)))
    return security.create_access_token(user.id)


def login(db: Session, email: str, password: str) -> str:
    user = _find_by_email(db, email.lower())
    # Same error for "no such user", "Google-only user" and "wrong password"
    if user is None or user.password_hash is None or not security.verify_password(password, user.password_hash):
        raise HTTPException(status_code=401, detail="Wrong email or password")
    return security.create_access_token(user.id)


def google_login(db: Session, id_token: str) -> str:
    if not settings.GOOGLE_CLIENT_ID:
        raise HTTPException(status_code=503, detail="Google sign-in isn't set up")

    identity = google_client.verify(id_token)
    if identity is None or not identity.email_verified:
        raise HTTPException(status_code=401, detail="Invalid Google sign-in")

    user = db.scalars(select(User).where(User.google_sub == identity.sub)).first()
    if user is None:
        # They may already have a password account with this email. Linking is safe
        # because Google says they own the address.
        user = _find_by_email(db, identity.email.lower())
        if user is None:
            user = User(email=identity.email.lower(), password_hash=None)
        user.google_sub = identity.sub
        db_helper.save(db, user)
    return security.create_access_token(user.id)


def _find_by_email(db: Session, email: str) -> User | None:
    return db.scalars(select(User).where(User.email == email)).first()
