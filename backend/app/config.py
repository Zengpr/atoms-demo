from pydantic_settings import BaseSettings
from typing import List
import json


class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite+aiosqlite:///./atoms_demo.db"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    OPENAI_API_KEY: str = ""
    OPENAI_BASE_URL: str = ""
    LLM_MODEL: str = "agnes-2.0-flash"
    MOCK_MODE: bool = False
    CORS_ORIGINS_STR: str = "http://localhost:3000"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    model_config = {"env_file": [".env", ".env.local"], "env_file_encoding": "utf-8"}

    @property
    def CORS_ORIGINS(self) -> List[str]:
        raw = self.CORS_ORIGINS_STR
        try:
            result = json.loads(raw)
            if isinstance(result, list):
                return result
        except (json.JSONDecodeError, TypeError):
            pass
        return [c.strip() for c in raw.split(",") if c.strip()]


settings = Settings()
