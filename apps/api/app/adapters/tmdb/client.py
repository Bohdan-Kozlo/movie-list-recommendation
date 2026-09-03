"""TMDB metadata adapter."""

import json
from typing import Any, cast
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import urlopen

from app.adapters.tmdb.mappers import parse_date, to_synced_title
from app.modules.catalog.domain import ExternalTitle
from app.modules.catalog.sync import SyncedTitle


class TmdbNotFoundError(RuntimeError):
    """TMDB reported that a requested title does not exist."""


class TmdbClient:
    """Small TMDB v3 client using the standard-library HTTP stack."""

    def __init__(self, api_key: str, base_url: str) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")

    def popular_ids(self, title_type: str, page: int) -> list[int]:
        payload = self._get(
            f"discover/{title_type}",
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
        return to_synced_title(payload, title_type)

    def search_titles(self, query: str, title_type: str | None) -> list[ExternalTitle]:
        title_types = [title_type] if title_type else ["movie", "tv"]
        matches: list[ExternalTitle] = []
        for current_type in title_types:
            payload = self._get(
                f"search/{current_type}",
                {"query": query, "include_adult": "false", "language": "en-US", "page": "1"},
            )
            for item in payload.get("results", [])[:6]:
                title = item.get("title") or item.get("name")
                if title and item.get("id"):
                    matches.append(
                        ExternalTitle(
                            tmdb_id=int(item["id"]),
                            title_type=current_type,
                            title=title,
                            release_date=parse_date(
                                item.get("release_date") or item.get("first_air_date")
                            ),
                            poster_path=item.get("poster_path"),
                        )
                    )
        return matches[:12]

    def _get(self, endpoint: str, parameters: dict[str, str]) -> dict[str, Any]:
        query = urlencode({**parameters, "api_key": self._api_key})
        try:
            with urlopen(f"{self._base_url}/{endpoint}?{query}", timeout=20) as response:  # noqa: S310
                payload = json.loads(response.read())
        except HTTPError as error:
            if error.code == 404:
                raise TmdbNotFoundError("TMDB title not found.") from error
            raise RuntimeError("TMDB request failed.") from error
        except URLError as error:
            raise RuntimeError("TMDB request failed.") from error
        if not isinstance(payload, dict):
            raise RuntimeError("TMDB returned a non-object response.")
        return cast(dict[str, Any], payload)
