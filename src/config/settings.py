from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./torah.db"

    # Debug
    debug: bool = False

    # Claude CLI
    claude_model: str = "sonnet"
    claude_timeout: int = 300  # Longer timeout for bulk requests
    bulk_size: int = 50  # Verses per bulk request

    # Sefaria
    sefaria_timeout: float = 30.0
    sefaria_delay: float = 0.5  # Delay between API calls

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
