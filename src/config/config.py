"""Configuration management."""

import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Application configuration."""

    # HuggingFace
    HUGGINGFACE_MODEL = os.getenv(
        "HUGGINGFACE_MODEL",
        "Qwen/Qwen2.5-1.5B-Instruct"
    )
