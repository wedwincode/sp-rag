from pathlib import Path
from uuid import uuid4, UUID

from pydantic import HttpUrl


class Document:
    def __init__(self, initial_url: str):
        self.initial_url = HttpUrl(initial_url)
        self.downloaded_path: Path | None = None
        self.preprocessed_path: Path | None = None
        self.text: str | None = None
        self.name: str | None = None
        self.chunks: list[Chunk] = []

    def __str__(self):

        return self._get_str()

    def __repr__(self):
        return self._get_str()

    def _get_str(self) -> str:
        return (
            f"Document("
            f"initial_url: {str(self.initial_url)}, "
            f"downloaded_path: {str(self.downloaded_path)}, "
            f"preprocessed_path: {str(self.preprocessed_path)}, "
            f"text: {len(self.text) if self.text else None}, "
            f"name: {self.name}, "
            f"chunks: {len(self.chunks)})"
        )


class Chunk:
    def __init__(self, text: str):
        self.id: UUID = uuid4()
        self.text: str = text


class Query:
    def __init__(self, text: str):
        self.text = text


class PreparedQuery(Query):
    pass


class Answer:
    def __init__(self, text: str):
        self.text = text


class FoundEmbedding:
    def __init__(self, text: str, document_name: str | None = None, document_url: str | None = None):
        self.text: str = text
        self.document_name: str | None = document_name
        self.document_url: str | None = document_url

    def __str__(self):
        return f"{self.text}\nИсточник: {self.document_name} ({self.document_url})"
