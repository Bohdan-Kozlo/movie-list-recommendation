"""TMDB metadata adapter."""

import json
from datetime import date
from typing import Any, cast
from urllib.parse import urlencode
from urllib.request import urlopen

from app.modules.catalog.sync import SyncedGenre, SyncedTitle


class TmdbClient:
    """Small TMDB v3 client using the standard-library HTTP stack."""

    def __init__(self, api_key: str, base_url: str) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")

    def popular_ids(self, title_type: str, page: int) -> list[int]:
        endpoint = f"discover/{title_type}"
        payload = self._get(
            endpoint,
            {
                "include_adult": "false",
                "language": "en-US",
                "page": str(page),
                "sort_by": "popularity.desc",
                "with_original_language": "en",
            },
        )
        return [int(item["id"]) for item in payload.get("results", [])]

    def title_details(self, title_type: str, tmdb_id: int) -> SyncedTitle:
        payload = self._get(
            f"{title_type}/{tmdb_id}",
            {"append_to_response": "credits,keywords,external_ids", "language": "en-US"},
        )
        release_date = _parse_date(payload.get("release_date") or payload.get("first_air_date"))
        runtime = payload.get("runtime")
        if runtime is None and payload.get("episode_run_time"):
            runtime = payload["episode_run_time"][0]
        credits = payload.get("credits", {})
        creators = payload.get("created_by", [])
        if title_type == "movie":
            creators = [
                member for member in credits.get("crew", []) if member.get("job") == "Director"
            ]
        keyword_payload = payload.get("keywords", {})
        keyword_items = keyword_payload.get("keywords", keyword_payload.get("results", []))
        return SyncedTitle(
            tmdb_id=int(payload["id"]),
            title_type=title_type,
            title=payload.get("title") or payload.get("name") or "Untitled",
            original_title=payload.get("original_title") or payload.get("original_name"),
            overview=payload.get("overview") or None,
            original_language=payload.get("original_language") or "en",
            release_date=release_date,
            runtime_minutes=int(runtime) if runtime else None,
            poster_path=payload.get("poster_path"),
            backdrop_path=payload.get("backdrop_path"),
            popularity=float(payload.get("popularity", 0)),
            vote_average=float(payload["vote_average"])
            if payload.get("vote_average") is not None
            else None,
            tagline=payload.get("tagline") or None,
            cast=[
                {"name": member["name"], "character": member.get("character", "")}
                for member in credits.get("cast", [])[:10]
                if member.get("name")
            ],
            creators=[member["name"] for member in creators if member.get("name")],
            keywords=[item["name"] for item in keyword_items if item.get("name")],
            genres=[
                SyncedGenre(id=int(item["id"]), name=item["name"])
                for item in payload.get("genres", [])
            ],
            imdb_id=payload.get("external_ids", {}).get("imdb_id"),
        )

    def _get(self, endpoint: str, parameters: dict[str, str]) -> dict[str, Any]:
        query = urlencode({**parameters, "api_key": self._api_key})
        with urlopen(f"{self._base_url}/{endpoint}?{query}", timeout=20) as response:  # noqa: S310
            payload = json.loads(response.read())
        if not isinstance(payload, dict):
            raise RuntimeError("TMDB returned a non-object response.")
        return cast(dict[str, Any], payload)


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return date.fromisoformat(value)
