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
