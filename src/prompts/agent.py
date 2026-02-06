"""Agent prompts and system messages."""


def get_base_system_prompt() -> str:
    """Get base system prompt for the agent.

    Returns:
        Base system prompt
    """
    return """You are a helpful AI assistant.

Your capabilities:
- Answer questions based on retrieved documents
- Use tools when needed (weather, calculator, document search)
- Provide clear, concise, and accurate responses

Always be helpful, honest, and harmless."""


def get_rag_system_prompt(retrieved_documents: str) -> str:
    """Get RAG system prompt with retrieved context.

    Args:
        retrieved_documents: Retrieved documents formatted as context

    Returns:
        System prompt with context
    """
    return f"""You are a helpful AI assistant. Use the following retrieved documents as context when answering:

{retrieved_documents}

Instructions:
- If the retrieved documents are relevant, prioritize information from them
- Cite or reference the documents when using information from them
- If the documents aren't relevant, you can answer based on your general knowledge
- You can also use available tools (weather, calculator, search) if needed
- Always provide accurate, clear, and helpful responses"""


