"""LLM model calling node."""

import asyncio
from src.states import ChatbotState


async def call_model(state: ChatbotState, llm_with_tools) -> ChatbotState:
    """Call LLM with current state.

    Args:
        state: Current chatbot state with message history
        llm_with_tools: LLM instance bound with tools

    Returns:
        Updated state with LLM response
    """
    messages = state["messages"]
    # Run blocking LLM call in a separate thread to avoid blocking the event loop
    response = await asyncio.to_thread(llm_with_tools.invoke, messages)
    return {"messages": [response]}
