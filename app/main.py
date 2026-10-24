import httpx
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.main_router import router
from app.core.database import Base, engine
from app.core.config import settings
from app.clients.places import PlacesClient

# Creates restaurant_tracker.db and tables on first run if they don't exist.
Base.metadata.create_all(bind=engine)

# Set up the app
app = FastAPI(title="World of Food")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(httpx.HTTPError)
def places_error_handler(request: Request, exc: httpx.HTTPError):
    return JSONResponse(status_code=502, content={"detail": "Couldn't reach the Places API"})


# Add the routes to it
app.include_router(router)


