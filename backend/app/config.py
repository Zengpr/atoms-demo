from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./atoms_demo.db"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = ""
    LLM_MODEL: str = "agnes-2.0-flash"
    MOCK_MODE: bool = False
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    model_config = {"env_file": [".env", ".env.local"], "env_file_encoding": "utf-8"}


settings = Settings()
