from pathlib import Path
from pydantic_settings import BaseSettings

_ENV_FILE = Path(__file__).parent / ".env"


class Settings(BaseSettings):
    NEWS_API_KEY: str
    CORS_ORIGINS: list[str] = ["http://localhost:5173"]
    TOP_N_HOLDINGS: int = 10
    CACHE_DIR: str = str(Path(__file__).parent / ".cache")
    HOLDINGS_CACHE_TTL: int = 86400   # 24 hours
    NEWS_CACHE_TTL: int = 1800        # 30 minutes

    model_config = {"env_file": str(_ENV_FILE)}


settings = Settings()
