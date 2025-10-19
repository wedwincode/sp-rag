import logging
from abc import ABC, abstractmethod

import yandex_cloud_ml_sdk.exceptions
from chromadb.api.models.AsyncCollection import AsyncCollection
from yandex_cloud_ml_sdk import YCloudML

from sp_rag.database import AbstractConnector
from sp_rag.models import Document, Query
from sp_rag.settings import get_settings
from sp_rag.utils.logs import setup_logger


class AbstractVectorizer(ABC):
    @abstractmethod
    async def vectorize_all(self) -> None:
        pass

    @abstractmethod
    async def _vectorize_one(self, document: Document, collection: AsyncCollection) -> None:
        pass

    @staticmethod
    @abstractmethod
    def vectorize_query(query: Query) -> list[float]:
        pass


class YandexVectorizer(AbstractVectorizer):
    logger: logging.Logger
    _log_file: str = "vectorizer.log"

    def __init__(self, documents: list[Document], db: AbstractConnector):
        self.documents = documents
        self.db = db
        self._sdk = YCloudML(folder_id=get_settings().YC_FOLDER_ID, auth=get_settings().YC_API_KEY)
        self.doc_model = self._sdk.models.text_embeddings("doc")

        if YandexVectorizer.logger is None:
            YandexVectorizer.logger = setup_logger("vectorizer", "vectorizer.log")
    @classmethod
    def set_log_file(cls, log_file: str):
        cls._log_file = log_file
        cls.logger = setup_logger("vectorizer", log_file)

    async def vectorize_all(self) -> None:
        collection = await self.db.get_collection("snip_chunks")
        for document in self.documents:
            await self._vectorize_one(document, collection)

    async def _vectorize_one(self, document: Document, collection: AsyncCollection) -> None:
        for i, chunk in enumerate(document.chunks):
            try:
                response = self.doc_model.run(chunk.text)  # todo async
                vector = list(response.embedding)
                self.logger.debug(f"Got response for chunk #{str(chunk.id)}")
                await collection.add(
                    ids=[str(chunk.id)],
                    documents=[chunk.text],
                    embeddings=vector,
                    metadatas=[{"document_name": document.name, "document_url": str(document.initial_url)}]
                )
                self.logger.debug(f"Vector for chunk #{str(chunk.id)} added to collection")
            except yandex_cloud_ml_sdk.exceptions.AioRpcError:
                self.logger.error(f"Chunk #{chunk.id} (size: {len(chunk.text)}) (text: {chunk.text[:300]}...)"
                                  f" caused an AioRpcException")

    @staticmethod
    def vectorize_query(query: Query) -> list[float]:
        _sdk = YCloudML(folder_id=get_settings().YC_FOLDER_ID, auth=get_settings().YC_API_KEY)
        query_model = _sdk.models.text_embeddings("query")
        response = query_model.run(query.text)
        return list(response.embedding)
