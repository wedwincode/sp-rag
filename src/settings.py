from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    YC_FOLDER_ID: str = ""
    YC_API_KEY: str = ""

    model_config = SettingsConfigDict(env_file="../.env")


settings = Settings()
