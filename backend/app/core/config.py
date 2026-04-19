"""
Application configuration using pydantic-settings.
All settings are loaded from environment variables or .env file.
"""

from typing import Literal
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    """
    Central configuration for MedScan AI.
    
    Design Decision: Using pydantic-settings so that:
    1. All config is validated at startup (fail fast)
    2. Switching LLM provider is a single env var change
    3. No hardcoded API keys anywhere in code
    """

    # ── LLM Provider Configuration ──────────────────────────────
    # Switch between providers with a single config change
    llm_provider: Literal["gemini", "groq", "ollama"] = "gemini"

    # Gemini (Google) — Free tier: 15 RPM, 1M tokens/day
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # Groq — Free tier: 30 RPM, runs Llama 3 70B
    groq_api_key: str = ""
    groq_model: str = "llama-3.3-70b-versatile"

    # Ollama (local) — No API key needed
    ollama_base_url: str = "http://localhost:11434"
    ollama_model: str = "llama3.2"

    # ── ChromaDB Configuration ──────────────────────────────────
    chroma_persist_dir: str = "./chroma_db"

    # ── Embedding Model ─────────────────────────────────────────
    embedding_model: str = "pritamdeka/S-PubMedBert-MS-MARCO"

    # ── App Settings ────────────────────────────────────────────
    debug: bool = True
    max_upload_size_mb: int = 10
    app_name: str = "MedScan AI"
    app_version: str = "0.1.0"

    # ── Database ────────────────────────────────────────────────
    database_url: str = "sqlite+aiosqlite:///./medscan.db"

    # ── Paths ───────────────────────────────────────────────────
    @property
    def knowledge_base_dir(self) -> Path:
        """Path to the medical knowledge base directory."""
        return Path(__file__).parent.parent / "knowledge"

    @property
    def upload_dir(self) -> Path:
        """Path to store uploaded reports."""
        path = Path(__file__).parent.parent.parent / "uploads"
        path.mkdir(exist_ok=True)
        return path

    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
    }


# Singleton — import this everywhere
settings = Settings()
