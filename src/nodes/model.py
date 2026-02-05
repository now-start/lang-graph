"""LLM model calling node."""

import asyncio
from langchain_core.messages import SystemMessage
from src.states.chatbot import ChatbotState
from src.prompts.agent import get_rag_system_prompt, get_base_system_prompt


async def call_model(state: ChatbotState, llm_with_tools) -> ChatbotState:
    """Call LLM with current state and retrieved context.

    Args:
        state: Current chatbot state with message history
        llm_with_tools: LLM instance bound with tools

    Returns:
        Updated state with LLM response
    """
    messages = state["messages"]

    # Add system prompt based on context availability
    retrieved_docs = state.get("retrieved_documents")
    if retrieved_docs:
        # Use RAG system prompt with retrieved context
        system_content = get_rag_system_prompt(retrieved_docs)
    else:
        # Use base system prompt
        system_content = get_base_system_prompt()

    # Prepend system message
    system_message = SystemMessage(content=system_content)
    messages_with_context = [system_message] + messages

    # Run blocking LLM call in a separate thread to avoid blocking the event loop
    response = await asyncio.to_thread(llm_with_tools.invoke, messages_with_context)
    return {"messages": [response]}
