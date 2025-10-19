import logging
from abc import ABC, abstractmethod

from yandex_cloud_ml_sdk import YCloudML

from sp_rag.database import AbstractConnector
from sp_rag.models import Query, PreparedQuery, Answer
from sp_rag.retriever import AbstractRetriever, Retriever
from sp_rag.settings import get_settings, StageEnum
from sp_rag.utils.logs import setup_logger


class AbstractGenerator(ABC):
    @abstractmethod
    async def generate_answer(self, query: Query) -> Answer:
        pass

    @abstractmethod
    async def _prepare_query(self, query: Query) -> PreparedQuery:
        pass


class Generator(AbstractGenerator):
    logger: logging.Logger
    _log_file: str = "generator.log"

    def __init__(self, db: AbstractConnector):
        self._retriever: AbstractRetriever = Retriever(db)
        self._sdk = YCloudML(folder_id=get_settings().YC_FOLDER_ID, auth=get_settings().YC_API_KEY)
        self.gpt_model = self._sdk.models.completions("yandexgpt")
        self.gpt_model.configure(temperature=0.3, max_tokens=600)

        if Generator.logger is None:
            Generator.logger = setup_logger("generator", "generator.log")

    @classmethod
    def set_log_file(cls, log_file: str):
        cls._log_file = log_file
        cls.logger = setup_logger("generator", log_file)

    async def generate_answer(self, query: Query) -> Answer:
        prepared = await self._prepare_query(query)
        answer_text = self.gpt_model.run(prepared.text).text
        return Answer(answer_text)

    async def _prepare_query(self, query: Query) -> PreparedQuery:
        embeddings = await self._retriever.get_embeddings_for_query(query)
        context_parts = [str(embedding) for embedding in embeddings]
        context_text = "\n\n".join(context_parts)
        prompt = f"""
        Вопрос пользователя: {query.text}
        
        Контекст из СНиПов/СП:
        {context_text}
        
        Ответь на вопрос, используя только эти данные. 
        В конце обязательно укажи источник.
        Если необходимая формула представлена в виде ссылки на изображение, то в ответе предоставь эту ссылку в формате markdown.
        """

        if get_settings().STAGE != StageEnum.PRODUCTION:
            self.logger.debug(f"Prompt: {prompt}")

        return PreparedQuery(prompt)
