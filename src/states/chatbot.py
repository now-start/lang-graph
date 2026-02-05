"""Chatbot state definition."""

from typing import TypedDict, Annotated, Optional
import operator


class ChatbotState(TypedDict, total=False):
    """State schema for chatbot.

    Attributes:
        input: Simple text input from user (optional)
        messages: Conversation history (accumulated with operator.add)
        retrieved_documents: Documents retrieved from Elasticsearch (for RAG)
        query: Current user query for retrieval
    """
    input: Optional[str]
    messages: Annotated[list, operator.add]
    retrieved_documents: Optional[str]
    query: Optional[str]
