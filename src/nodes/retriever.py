"""Document retrieval node for RAG."""

import logging

from src.states.chatbot import ChatbotState
from src.tools.retriever import get_retriever

logger = logging.getLogger(__name__)


def retrieve_documents(state: ChatbotState) -> dict:
    """Retrieve relevant documents for RAG.

    Args:
        state: Current chatbot state

    Returns:
        Updated state with retrieved documents
    """
    # Extract query from latest user message
    messages = state.get("messages", [])
    if not messages:
        return {"retrieved_documents": ""}

    # Get the last human message as query
    query = None
    for msg in reversed(messages):
        if hasattr(msg, "type") and msg.type == "human":
            query = msg.content
            break
        if isinstance(msg, dict) and msg.get("role") == "user":
            query = msg.get("content", "")
            break

    if not query:
        return {"retrieved_documents": ""}

    try:
        # Retrieve documents
        retriever = get_retriever()
        docs = retriever.invoke(query)

        if not docs:
            return {
                "retrieved_documents": "",
                "query": query,
            }

        # Format documents as context
        context_parts = ["Retrieved Documents:\n"]
        for i, doc in enumerate(docs[:5], 1):  # Limit to top 5
            content = doc.page_content[:500]  # Limit length
            context_parts.append(f"{i}. {content}\n")

        retrieved_context = "\n".join(context_parts)

        return {
            "retrieved_documents": retrieved_context,
            "query": query,
        }

    except Exception as e:
        logger.exception("Retrieval error: %s", e)
        return {
            "retrieved_documents": f"Retrieval failed: {str(e)}",
            "query": query,
        }
