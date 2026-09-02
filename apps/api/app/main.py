from os import getenv

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.modules.catalog.api import router as catalogue_router

app = FastAPI(title="Movie List Recommendation API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=getenv("WEB_ORIGINS", "http://localhost:5173").split(","),
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=[],
)
app.include_router(catalogue_router)


@app.get("/health")
async def health() -> dict[str, str]:
    """Report whether the API process is ready to receive requests."""
    return {"status": "ok"}
