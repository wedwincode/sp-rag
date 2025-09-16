from abc import ABC, abstractmethod

from chromadb import AsyncHttpClient
from chromadb.api import AsyncClientAPI
from chromadb.api.models.AsyncCollection import AsyncCollection
from chromadb.config import Settings


class AbstractConnector(ABC):

    @abstractmethod
    async def _get_connector(self) -> AsyncClientAPI:
        pass

    @abstractmethod
    async def get_collection(self, collection_name: str) -> AsyncCollection:  # todo: async collection is chromadb class
        pass

    @abstractmethod
    async def delete_collection(self, collection_name: str) -> None:
        pass


class ChromaDBConnectorAsync(AbstractConnector):
    def __init__(self, host: str = "localhost", port: int = 8000):
        self.host = host
        self.port = port
        self._client: AsyncClientAPI | None = None

    async def _get_connector(self) -> AsyncClientAPI:
        if not self._client:
            self._client = await AsyncHttpClient(
                host=self.host,
                port=self.port,
                settings=Settings(anonymized_telemetry=False)
            )
        return self._client

    async def get_collection(self, collection_name: str) -> AsyncCollection:
        client = await self._get_connector()
        return await client.get_or_create_collection(collection_name)

    async def delete_collection(self, collection_name: str) -> None:
        client = await self._get_connector()
        return await client.delete_collection(collection_name)
