"""LLM initialization utilities."""

from langchain_ollama import ChatOllama
from src.config.config import Config


def get_local_llm() -> ChatOllama:
    """Initialize local Ollama model.

    Returns:
        ChatOllama: Initialized chat language model
    """
    model_id = Config.OLLAMA_MODEL
    base_url = Config.OLLAMA_BASE_URL

    print(f"🔄 Connecting to Ollama: {model_id} at {base_url}")

    chat_model = ChatOllama(
        model=model_id,
        base_url=base_url,
        temperature=0.7,
        keep_alive=0,  # 즉시 언로드
        num_ctx=2048,
    )
    print("✅ Model connected successfully!\n")

    return chat_model