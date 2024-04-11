import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    OMDP_API_KEY: str = os.getenv("OMDP_API_KEY")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY")
    QDRANT_URL: str = os.getenv("QDRANT_URL")


settings = Settings()
