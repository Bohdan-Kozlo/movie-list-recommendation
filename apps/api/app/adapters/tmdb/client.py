"""TMDB metadata adapter."""

import json
from typing import Any, cast
from urllib.parse import urlencode
from urllib.request import urlopen

from app.adapters.tmdb.mappers import to_synced_title
from app.modules.catalog.sync import SyncedTitle


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

    def _get(self, endpoint: str, parameters: dict[str, str]) -> dict[str, Any]:
        query = urlencode({**parameters, "api_key": self._api_key})
        with urlopen(f"{self._base_url}/{endpoint}?{query}", timeout=20) as response:  # noqa: S310
            payload = json.loads(response.read())
        if not isinstance(payload, dict):
            raise RuntimeError("TMDB returned a non-object response.")
        return cast(dict[str, Any], payload)
