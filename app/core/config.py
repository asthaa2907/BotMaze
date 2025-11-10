# app/core/config.py

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuration class for BotMaze multi-user version.
    Stores only global/static variables.
    """

    # ✅ WhatsApp webhook verification token (used only once when Meta verifies your webhook)
    WHATSAPP_VERIFY_TOKEN: str

    # ✅ LLM & embedding configuration
    groq_api_key: str
    llm_model: str = "llama3-8b-8192"
    embed_model: str = "sentence-transformers/all-MiniLM-L6-v2"

    # ✅ Vector database
    qdrant_url: str
    qdrant_api_key: str | None = None

    # ✅ Optional environment flags
    environment: str = "development"
    debug: bool = True

    class Config:
        env_file = ".env"


# Global settings instance
settings = Settings()
