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
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    model_config = {"env_file": [".env", ".env.local"], "env_file_encoding": "utf-8"}

    @classmethod
    def customize_sources(cls, settings_cls, init_settings, env_settings, dotenv_settings, file_secret_settings):
        return (init_settings, env_settings, dotenv_settings, file_secret_settings)


def _parse_cors():
    import os
    cors = os.environ.get("CORS_ORIGINS", "")
    if cors:
        try:
            return json.loads(cors)
        except (json.JSONDecodeError, TypeError):
            return [c.strip() for c in cors.split(",") if c.strip()]
    return ["http://localhost:3000"]


settings = Settings()
settings.CORS_ORIGINS = _parse_cors()
