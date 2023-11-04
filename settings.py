import os

from pydantic_settings import BaseSettings

if not os.environ.get("PRODUCTION"):
    import dotenv

    dotenv.load_dotenv(dotenv.find_dotenv())


class Settings(BaseSettings):
    CLAUDE_API_KEY: str


settings = Settings()
