from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from os import getenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.core.database import dispose_database_engines
from app.modules.auth.api import router as auth_router
from app.modules.catalog.api import router as catalogue_router
from app.modules.interactions.api import router as interactions_router
from app.modules.onboarding.api import router as onboarding_router
from app.modules.recommendations.api import router as recommendations_router

app_environment = getenv("APP_ENV", "development")
oauth_state_secret = getenv("AUTH_SESSION_SECRET")
if not oauth_state_secret:
    if app_environment != "development":
        raise RuntimeError("AUTH_SESSION_SECRET must be configured outside development.")
    oauth_state_secret = "development-only-oauth-state-secret"


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncIterator[None]:
    try:
        yield
    finally:
        dispose_database_engines()


app = FastAPI(title="Movie List Recommendation API", lifespan=lifespan)
app.add_middleware(
    SessionMiddleware,
    secret_key=oauth_state_secret,
    https_only=getenv("AUTH_COOKIE_SECURE", "false").lower() == "true",
    same_site="lax",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=getenv("WEB_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=True,
    allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type"],
)
app.include_router(catalogue_router)
app.include_router(auth_router)
app.include_router(interactions_router)
app.include_router(onboarding_router)
app.include_router(recommendations_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Report whether the API process is ready to receive requests."""
    return {"status": "ok"}
