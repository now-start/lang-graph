"""Input processing node."""

from langchain_core.messages import HumanMessage
from src.states.chatbot import ChatbotState


def process_input(state: ChatbotState) -> dict:
    """Convert text input to messages if provided.

    Args:
        state: Current chatbot state

    Returns:
        Updated state with messages
    """
    # If input field exists, convert to message
    if "input" in state and state["input"]:
        return {
            "messages": [HumanMessage(content=state["input"])]
        }

    # Otherwise, messages should already exist
    return {}
