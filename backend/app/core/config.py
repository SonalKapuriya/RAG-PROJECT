# ─────────────────────────────────────────────
# All environment variables and app-wide config
# ─────────────────────────────────────────────
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    # API Keys
    GROQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    HUGGINGFACE_API_KEY: str = ""

    # Qdrant
    QDRANT_URL: str = "http://localhost:6333"
    QDRANT_API_KEY: str | None = None
    COLLECTION_NAME: str = "hr_resumes"

    # Embedding model — fixed, not dynamic
    EMBED_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"
    VECTOR_SIZE: int = 384

    # Resumes folder
    RESUMES_FOLDER: str = "./resumes"

    # App
    APP_NAME: str = "RecruitAI"
    VERSION: str = "1.0.0"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()