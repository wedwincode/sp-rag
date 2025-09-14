from enum import Enum

from pydantic_settings import BaseSettings, SettingsConfigDict


class StageEnum(str, Enum):
    PRODUCTION = "PRODUCTION"
    STAGING = "STAGING"
    LOCAL = "LOCAL"


class Settings(BaseSettings):
    YC_FOLDER_ID: str = ""
    YC_API_KEY: str = ""
    STAGE: StageEnum = StageEnum.LOCAL

    model_config = SettingsConfigDict(env_file="../.env")


settings = Settings()
