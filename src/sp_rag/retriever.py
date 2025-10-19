import logging
from abc import ABC, abstractmethod

from sp_rag.database import AbstractConnector
from sp_rag.models import Query, FoundEmbedding
from sp_rag.utils.logs import setup_logger
from sp_rag.vectorizer import YandexVectorizer


class AbstractRetriever(ABC):
    @abstractmethod
    async def get_embeddings_for_query(self, query: Query) -> list[FoundEmbedding]:
        pass


class Retriever(AbstractRetriever):
    logger: logging.Logger
    _log_file: str = "retriever.log"

    def __init__(self, db: AbstractConnector):
        self.db = db

        if Retriever.logger is None:
            Retriever.logger = setup_logger("retriever", "retriever.log")

    @classmethod
    def set_log_file(cls, log_file: str):
        cls._log_file = log_file
        cls.logger = setup_logger("retriever", log_file)

    async def get_embeddings_for_query(self, query: Query, size: int = 4) -> list[FoundEmbedding]:
        vector = YandexVectorizer.vectorize_query(query)
        collection = await self.db.get_collection("snip_chunks")

        search_results = await collection.query(
            query_embeddings=vector,
            n_results=size,
            include=["documents", "metadatas"]
        )

        found: list[FoundEmbedding] = []
        documents = search_results.get("documents")
        metadatas = search_results.get("metadatas")
        if documents and metadatas:
            for doc, meta in zip(documents[0], metadatas[0]):
                document_name = str(meta.get("document_name"))
                document_url = str(meta.get("document_url"))
                found.append(FoundEmbedding(doc, document_name, document_url))
        return found
