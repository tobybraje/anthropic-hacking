import os

from pydantic_settings import BaseSettings
import dotenv

dotenv.load_dotenv(dotenv.find_dotenv())


class Settings(BaseSettings):
    ANTHROPIC_API_KEY: str
    DSM_PATH: str


settings = Settings()
