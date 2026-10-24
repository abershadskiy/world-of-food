from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.dependencies import get_current_user
from app.dto.auth import Credentials, GoogleLoginRequest, LoginRequest, Token
from app.dto.user import User
from app.models import User as UserModel
from app.services import auth

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


@router.post("/signup", response_model=Token)
def signup(credentials: Credentials, db: Session = Depends(get_db)):
    return Token(access_token=auth.signup(db, credentials.email, credentials.password))


@router.post("/login", response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    return Token(access_token=auth.login(db, credentials.email, credentials.password))


@router.post("/google", response_model=Token)
def google_login(body: GoogleLoginRequest, db: Session = Depends(get_db)):
    return Token(access_token=auth.google_login(db, body.id_token))


@router.get("/me", response_model=User)
def me(current_user: UserModel = Depends(get_current_user)):
    return current_user
