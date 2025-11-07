import os
from typing import Optional
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    """Application settings"""

    # API keys and external services
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    QDRANT_URL: str = os.getenv("QDRANT_URL", "http://localhost:6333")
    QDRANT_API_KEY: Optional[str] = os.getenv("QDRANT_API_KEY")

    # Vector database settings
    COLLECTION_NAME: str = os.getenv("COLLECTION_NAME", "articles")
    TOP_K_RESULTS: int = int(os.getenv("TOP_K_RESULTS", "5"))

    # Relevance filtering settings
    MIN_RELEVANCE_SCORE: float = float(os.getenv("MIN_RELEVANCE_SCORE", "0.75"))
    HIGH_RELEVANCE_THRESHOLD: float = float(os.getenv("HIGH_RELEVANCE_THRESHOLD", "0.85"))

    # API settings
    API_TITLE: str = "AI Journalist Assistant"
    API_DESCRIPTION: str = "AI-powered tool for journalists to research and draft evidence-backed articles"
    API_VERSION: str = "0.1.0"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

# Create a global settings instance
settings = Settings()