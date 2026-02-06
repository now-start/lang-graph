"""LLM initialization utilities."""

import logging

from langchain_ollama import ChatOllama
from src.config.config import Config

logger = logging.getLogger(__name__)


def get_local_llm() -> ChatOllama:
    """Initialize local Ollama model.

    Returns:
        ChatOllama: Initialized chat language model
    """
    model_id = Config.OLLAMA_MODEL
    base_url = Config.OLLAMA_BASE_URL

    logger.info("Connecting to Ollama: %s at %s", model_id, base_url)

    chat_model = ChatOllama(
        model=model_id,
        base_url=base_url,
        temperature=0.7,
        keep_alive=0,
        num_ctx=2048,
    )
    logger.info("Model connected successfully.")

    return chat_model
