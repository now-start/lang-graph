"""Chatbot state definition."""

from typing import TypedDict, Annotated
import operator


class ChatbotState(TypedDict):
    """State schema for chatbot.

    Attributes:
        messages: Conversation history (accumulated with operator.add)
    """
    messages: Annotated[list, operator.add]
