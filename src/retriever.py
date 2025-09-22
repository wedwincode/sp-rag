from abc import ABC, abstractmethod

from src.database import AbstractConnector
from src.models import Query, FoundEmbedding
from src.utils.logs import setup_logger
from src.vectorizer import YandexVectorizer


class AbstractRetriever(ABC):
    @abstractmethod
    async def get_embeddings_for_query(self, query: Query) -> list[FoundEmbedding]:
        pass


class Retriever(AbstractRetriever):
    logger = setup_logger("retriever", "../logs/retriever.log")

    def __init__(self, db: AbstractConnector):
        self.db = db

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
