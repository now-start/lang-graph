"""LLM initialization utilities."""

from langchain_ollama import ChatOllama
from src.config.config import Config


# Global variable to cache the model
_chat_model = None


def get_local_llm() -> ChatOllama:
    """Initialize local Ollama model.

    Returns:
        ChatOllama: Initialized chat language model
    """
    global _chat_model

    if _chat_model is not None:
        print("reusing cached model...")
        return _chat_model

    model_id = Config.OLLAMA_MODEL
    base_url = Config.OLLAMA_BASE_URL

    print(f"🔄 Connecting to Ollama: {model_id} at {base_url}")

    _chat_model = ChatOllama(
        model=model_id,
        base_url=base_url,
        temperature=0.7,
    )
    print("✅ Model connected successfully!\n")

    return _chat_model
