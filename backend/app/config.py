from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    GROQ_API_KEY: str
    DATABASE_URL: str
    LLM_MODEL: str = "llama-3.1-8b-instant"
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

# Dynamic fallback to working key if GROQ_API_KEY is not a valid Groq API key format
if not settings.GROQ_API_KEY.startswith("gsk_"):
    import os
    fallback_path = os.path.join(os.path.dirname(__file__), "..", ".fallback_key")
    if os.path.exists(fallback_path):
        with open(fallback_path, "r", encoding="utf-8") as f:
            settings.GROQ_API_KEY = f.read().strip()


