"""AI Chatbot graph configuration.

This module defines the chatbot graph structure:
- Node connections
- Conditional edges
- State schema

Node implementations are in src/nodes/chatbot/
"""

import asyncio
from functools import partial
from langgraph.graph import StateGraph, END

from langchain_ollama import ChatOllama
from src.states import ChatbotState
from src.tools import get_weather, calculate
from src.utils import get_local_llm
from src.nodes import call_model, call_tools, should_continue


async def create_chatbot_graph():
    """Create and configure the chatbot graph.

    Graph structure:
        agent → [conditional] → tools → agent
                             ↓
                            end

    Returns:
        Compiled StateGraph ready for execution
    """
    # Initialize LLM with tools
    tools = [get_weather, calculate]
    # Use to_thread to avoid blocking event loop during heavy model loading
    chat_model: ChatOllama = await asyncio.to_thread(get_local_llm)
    # Ensure tool binding is correct for Qwen
    chat_model_with_tools = chat_model.bind_tools(tools)

    # Create graph
    workflow = StateGraph(ChatbotState)

    # Add nodes (bind LLM to call_model using partial)
    workflow.add_node("agent", partial(call_model, llm_with_tools=chat_model_with_tools))
    workflow.add_node("tools", call_tools)

    # Configure edges
    workflow.set_entry_point("agent")
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tools": "tools",
            "end": END
        }
    )
    workflow.add_edge("tools", "agent")

    return workflow.compile()


# Global variable to cache the compiled graph
_compiled_graph = None


async def graph():
    """Lazy graph initialization for LangGraph Dev."""
    global _compiled_graph
    if _compiled_graph is None:
        _compiled_graph = await create_chatbot_graph()
    return _compiled_graph
