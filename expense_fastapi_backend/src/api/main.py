from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from src.core.config import get_settings
from src.core.database import get_db
from src.api.routers_auth import router as auth_router
from src.api.routers_categories import router as categories_router
from src.api.routers_expenses import router as expenses_router

settings = get_settings()

openapi_tags = [
    {"name": "Health", "description": "Service health and diagnostics"},
    {"name": "Auth", "description": "Authentication endpoints (signup, login, current user)"},
    {"name": "Categories", "description": "CRUD for user-owned categories"},
    {"name": "Expenses", "description": "CRUD for user-owned expenses"},
]

app = FastAPI(
    title=settings.APP_NAME,
    description=settings.APP_DESCRIPTION,
    version=settings.APP_VERSION,
    openapi_tags=openapi_tags,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Health"], summary="Health Check", description="Simple service liveness probe.")
def health_check():
    """Health check endpoint returning a simple JSON."""
    return {"message": "Healthy"}


@app.get(
    "/db-ping",
    tags=["Health"],
    summary="Database Ping",
    description="Ensures the database connection is reachable by executing a simple SQL statement.",
)
def db_ping(db: Session = Depends(get_db)):
    """Ping the database by executing 'SELECT 1'."""
    db.execute("SELECT 1")
    return {"database": "ok"}


# Include routers
app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(expenses_router)
