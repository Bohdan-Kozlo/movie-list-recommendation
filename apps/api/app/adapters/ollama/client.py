"""Ollama embedding adapter backed by the official Python SDK."""

from ollama import Client, RequestError, ResponseError


class OllamaEmbeddingClient:
    def __init__(self, base_url: str, model: str) -> None:
        self._client = Client(host=base_url, timeout=30)
        self._model = model

    def embed(self, text: str) -> list[float]:
        try:
            response = self._client.embed(model=self._model, input=text)
        except (ConnectionError, RequestError, ResponseError) as error:
            raise RuntimeError("Ollama embedding request failed.") from error
        if not response.embeddings:
            raise RuntimeError("Ollama returned no embedding vector.")
        return list(response.embeddings[0])
