from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.clients.places import PlacesClient
from app.core import security
from app.core.database import get_db
from app.models import User

# Create clients
places_client = PlacesClient()

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_user(
        credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
        db: Session = Depends(get_db)
) -> User:
    user_id = security.read_access_token(credentials.credentials) if credentials else None
    user = db.get(User, user_id) if user_id else None
    if user is None:
        raise HTTPException(
            status_code=401, detail="Not logged in", headers={"WWW-Authenticate": "Bearer"}
        )
    return user


def get_user_or_404(user_id: int, current_user: User = Depends(get_current_user)) -> User:
    # Users can only see their own data. 404 rather than 403 so ids can't be probed.
    if user_id != current_user.id:
        raise HTTPException(status_code=404, detail=f"User {user_id} not found")
    return current_user
