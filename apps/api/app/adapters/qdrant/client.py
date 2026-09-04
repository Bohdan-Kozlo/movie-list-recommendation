"""Qdrant Cloud adapter backed by the official Python SDK."""

from typing import Any

from qdrant_client import QdrantClient as QdrantSdkClient
from qdrant_client.http.exceptions import ApiException
from qdrant_client.models import (
    Distance,
    FieldCondition,
    Filter,
    HasIdCondition,
    MatchValue,
    PointStruct,
    VectorParams,
)


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

    def search(
        self,
        vector: list[float],
        limit: int,
        excluded_id: str | None = None,
        title_type: str | None = None,
        excluded_ids: set[str] | None = None,
    ) -> list[str]:
        try:
            must: list[Any] | None = (
                [FieldCondition(key="type", match=MatchValue(value=title_type))]
                if title_type is not None
                else None
            )
            excluded = set(excluded_ids or set())
            if excluded_id is not None:
                excluded.add(excluded_id)
            must_not: list[Any] | None = (
                [HasIdCondition(has_id=sorted(excluded))] if excluded else None
            )
            response = self._client.query_points(
                collection_name=self._collection,
                query=vector,
                limit=limit,
                with_payload=["title_id"],
                query_filter=Filter(must=must, must_not=must_not),
            )
        except ApiException as error:
            raise RuntimeError("Qdrant semantic search failed.") from error
        return [
            str(payload["title_id"])
            for point in response.points
            if (payload := point.payload) and payload.get("title_id")
        ]
