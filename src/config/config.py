"""Configuration management."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""

    # Ollama
    OLLAMA_MODEL = os.getenv(
        "OLLAMA_MODEL",
        "qwen3:4b"
    )
    OLLAMA_EMBEDDING_MODEL = os.getenv(
        "OLLAMA_EMBEDDING_MODEL",
        "qwen3-embedding:0.6b"
    )
    OLLAMA_BASE_URL = os.getenv(
        "OLLAMA_BASE_URL",
        "http://localhost:11434"
    )

    # Elasticsearch
    ELASTICSEARCH_URL = os.getenv(
        "ELASTICSEARCH_URL",
        "http://localhost:9200"
    )
    ELASTICSEARCH_INDEX = os.getenv(
        "ELASTICSEARCH_INDEX",
        "documents"
    )
    ELASTICSEARCH_API_KEY = os.getenv("ELASTICSEARCH_API_KEY")
    ELASTICSEARCH_USER = os.getenv("ELASTICSEARCH_USER")
    ELASTICSEARCH_PASSWORD = os.getenv("ELASTICSEARCH_PASSWORD")
