"""Qdrant Cloud adapter backed by the official Python SDK."""

from typing import Any

from qdrant_client import QdrantClient as QdrantSdkClient
from qdrant_client.http.exceptions import ApiException
from qdrant_client.models import Distance, Filter, HasIdCondition, PointStruct, VectorParams


class QdrantClient:
    def __init__(self, base_url: str, api_key: str, collection: str) -> None:
        self._client = QdrantSdkClient(url=base_url, api_key=api_key, timeout=30)
        self._collection = collection

    def upsert(self, point_id: str, vector: list[float], payload: dict[str, Any]) -> None:
        try:
            if not self._client.collection_exists(self._collection):
                self._client.create_collection(
                    collection_name=self._collection,
                    vectors_config=VectorParams(size=len(vector), distance=Distance.COSINE),
                )
            self._client.upsert(
                collection_name=self._collection,
                points=[PointStruct(id=point_id, vector=vector, payload=payload)],
            )
        except ApiException as error:
            raise RuntimeError("Qdrant vector upsert failed.") from error

    def search(self, vector: list[float], limit: int, excluded_id: str) -> list[str]:
        try:
            response = self._client.query_points(
                collection_name=self._collection,
                query=vector,
                limit=limit,
                with_payload=["title_id"],
                query_filter=Filter(must_not=[HasIdCondition(has_id=[excluded_id])]),
            )
        except ApiException as error:
            raise RuntimeError("Qdrant semantic search failed.") from error
        return [
            str(payload["title_id"])
            for point in response.points
            if (payload := point.payload) and payload.get("title_id")
        ]
