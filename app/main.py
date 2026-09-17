from fastapi import FastAPI

from app.api.main_router import router
from app.core.database import Base, engine
from app.core.config import settings
from app.clients.places import PlacesClient

# Creates restaurant_tracker.db and tables on first run if they don't exist.
Base.metadata.create_all(bind=engine)

# Set up the app
app = FastAPI(title="World of Food")

# Add the routes to it
app.include_router(router)


