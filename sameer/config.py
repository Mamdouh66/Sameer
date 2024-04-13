import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    OMDP_API_KEY: str = os.getenv("OMDP_API_KEY")
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    QDRANT_API_KEY: str = os.getenv("QDRANT_API_KEY")
    QDRANT_URL: str = os.getenv("QDRANT_URL")

    ID_MAPPING_DATASET_PATH: str = (
        "/Users/mamdouh/Developer/filmora/data/id_to_imdb_id.csv"  # TODO: TO VM settings
    )


settings = Settings()
