from fastapi import FastAPI

app = FastAPI(title="Movie List Recommendation API")


@app.get("/health")
async def health() -> dict[str, str]:
    """Report whether the API process is ready to receive requests."""
    return {"status": "ok"}
