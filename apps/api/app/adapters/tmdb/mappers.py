"""Mappings from TMDB payloads to normalized synchronization values."""

from datetime import date
from typing import Any

from app.modules.catalog.sync import SyncedGenre, SyncedTitle


def to_synced_title(payload: dict[str, Any], title_type: str) -> SyncedTitle:
    runtime = payload.get("runtime")
    if runtime is None and payload.get("episode_run_time"):
        runtime = payload["episode_run_time"][0]
    credits = payload.get("credits", {})
    creators = payload.get("created_by", [])
    if title_type == "movie":
        creators = [member for member in credits.get("crew", []) if member.get("job") == "Director"]
    keyword_payload = payload.get("keywords", {})
    keyword_items = keyword_payload.get("keywords", keyword_payload.get("results", []))
    return SyncedTitle(
        tmdb_id=int(payload["id"]),
        title_type=title_type,
        title=payload.get("title") or payload.get("name") or "Untitled",
        original_title=payload.get("original_title") or payload.get("original_name"),
        overview=payload.get("overview") or None,
        original_language=payload.get("original_language") or "en",
        release_date=parse_date(payload.get("release_date") or payload.get("first_air_date")),
        runtime_minutes=int(runtime) if runtime else None,
        poster_path=payload.get("poster_path"),
        backdrop_path=payload.get("backdrop_path"),
        popularity=float(payload.get("popularity", 0)),
        vote_average=(
            float(payload["vote_average"]) if payload.get("vote_average") is not None else None
        ),
        tagline=payload.get("tagline") or None,
        cast=[
            {"name": member["name"], "character": member.get("character", "")}
            for member in credits.get("cast", [])[:10]
            if member.get("name")
        ],
        creators=[member["name"] for member in creators if member.get("name")],
        keywords=[item["name"] for item in keyword_items if item.get("name")],
        genres=[
            SyncedGenre(id=int(item["id"]), name=item["name"]) for item in payload.get("genres", [])
        ],
        imdb_id=payload.get("external_ids", {}).get("imdb_id"),
    )


def parse_date(value: str | None) -> date | None:
    return date.fromisoformat(value) if value else None
