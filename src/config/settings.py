from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Database
    database_url: str = "sqlite:///./torah.db"
    database_path: str = "./data/talmud.db"

    # Debug
    debug: bool = False
    log_level: str = "info"

    # Claude CLI
    claude_model: str = "sonnet"
    claude_timeout: int = 300  # Longer timeout for bulk requests
    bulk_size: int = 50  # Verses per bulk request
    llm_provider: str = "parallel-cli"

    # Sefaria
    sefaria_timeout: float = 30.0
    sefaria_delay: float = 0.5  # Delay between API calls

    # Turso
    turso_database_url: Optional[str] = None
    turso_auth_token: Optional[str] = None

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "extra": "ignore"
    }


settings = Settings()
