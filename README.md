# Movie List Recommendation

## Catalogue development

Configure `.env` from `.env.example`, then start PostgreSQL with `docker compose --env-file .env --profile dependencies up -d postgres`.

Apply canonical-catalogue migrations explicitly:

```powershell
$env:DATABASE_URL = "postgresql://movie_app:change-me-for-local-development@localhost:5432/movie_recommendation"
uv run --group dev alembic -c apps/api/alembic.ini upgrade head
```

Set `TMDB_API_KEY` to a TMDB v3 API key and synchronize the initial catalogue:

```powershell
uv run recsys catalog sync
```

The sync imports five popularity-sorted discovery pages each for English movies and TV series. Re-running it updates the existing canonical records rather than creating duplicates.

## Authentication development

Set `AUTH_JWT_SECRET` and `AUTH_SESSION_SECRET` to long random values in `.env`. For Google sign-in, create a Google OpenID Connect web client and configure `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET`, and the exact `GOOGLE_REDIRECT_URI` registered with Google (locally, `http://localhost:8000/auth/google/callback`).

Apply the authentication migration with the existing Alembic command. The SPA uses HttpOnly access and refresh cookies; set `AUTH_COOKIE_SECURE=true` when it is served over HTTPS.
