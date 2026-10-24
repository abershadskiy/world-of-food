from dataclasses import dataclass

from google.auth.exceptions import GoogleAuthError
from google.auth.transport import requests
from google.oauth2 import id_token

from app.core.config import settings


@dataclass
class GoogleIdentity:
    sub: str
    email: str
    email_verified: bool


class GoogleAuthClient:
    def verify(self, token: str) -> GoogleIdentity | None:
        try:
            claims = id_token.verify_oauth2_token(token, requests.Request(), settings.GOOGLE_CLIENT_ID)
        except (ValueError, GoogleAuthError):
            return None
        return GoogleIdentity(
            sub=claims["sub"],
            email=claims.get("email", ""),
            email_verified=claims.get("email_verified", False),
        )
