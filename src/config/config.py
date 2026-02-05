"""Configuration management."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""

    # Ollama
    OLLAMA_MODEL = os.getenv(
        "OLLAMA_MODEL",
        "qwen3-vl:8b"
    )
    OLLAMA_BASE_URL = os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434"
    )
