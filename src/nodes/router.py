"""Routing logic for chatbot flow."""

from typing import Literal

from src.states.chatbot import ChatbotState


def should_continue(state: ChatbotState) -> Literal["tools", "end"]:
    """Route based on whether LLM wants to use tools.

    Args:
        state: Current chatbot state

    Returns:
        "tools" if LLM wants to call tools, "end" otherwise
    """
    messages = state["messages"]
    last_message = messages[-1]

    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "end"
