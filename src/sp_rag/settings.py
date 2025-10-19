from enum import Enum
from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class StageEnum(str, Enum):
    PRODUCTION = "PRODUCTION"
    STAGING = "STAGING"
    LOCAL = "LOCAL"


class Settings(BaseSettings):
    YC_FOLDER_ID: str = ""
    YC_API_KEY: str = ""
    STAGE: StageEnum = StageEnum.LOCAL
    CHROMA_DB_HOST: str = "localhost"
    CHROMA_DB_PORT: int = 8000

    model_config = SettingsConfigDict()


@lru_cache
def get_settings() -> Settings:
    return Settings()
