from abc import ABC, abstractmethod

from chromadb.api.models.AsyncCollection import AsyncCollection
from yandex_cloud_ml_sdk import YCloudML

from src.database import AbstractConnector
from src.models import Document, Query
from src.settings import settings
from src.utils.logs import setup_logger


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
    logger = setup_logger("vectorizer", "../logs/vectorizer.log")

    def __init__(self, documents: list[Document], db: AbstractConnector):
        self.documents = documents
        self.db = db
        self._sdk = YCloudML(folder_id=settings.YC_FOLDER_ID, auth=settings.YC_API_KEY)
        self.doc_model = self._sdk.models.text_embeddings("doc")

    async def vectorize_all(self) -> None:
        collection = await self.db.get_collection("snip_chunks")
        for document in self.documents:
            await self._vectorize_one(document, collection)

    async def _vectorize_one(self, document: Document, collection: AsyncCollection) -> None:
        for i, chunk in enumerate(document.chunks):
            response = self.doc_model.run(chunk.text) # todo async
            vector = list(response.embedding)
            self.logger.debug(f"Got response for chunk #{str(chunk.id)}")
            await collection.add(
                ids=[str(chunk.id)],
                documents=[chunk.text],
                embeddings=vector,
                metadatas=[{"document_name": document.name, "document_url": str(document.initial_url)}]
            )
            self.logger.debug(f"Vector for chunk #{str(chunk.id)} added to collection")

    @staticmethod
    def vectorize_query(query: Query) -> list[float]:
        _sdk = YCloudML(folder_id=settings.YC_FOLDER_ID, auth=settings.YC_API_KEY)
        query_model = _sdk.models.text_embeddings("query")
        response = query_model.run(query.text)
        return list(response.embedding)
