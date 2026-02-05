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
from langchain_core.messages import HumanMessage

from langchain_ollama import ChatOllama
from src.states.chatbot import ChatbotState
from src.tools.weather import get_weather
from src.tools.calculator import calculate
from src.tools.retriever import search_documents
from src.utils.llm import get_local_llm
from src.nodes.model import call_model
from src.nodes.tools_executor import call_tools
from src.nodes.router import should_continue
from src.nodes.input_processor import process_input
from src.nodes.retriever import retrieve_documents
from src.utils.docker import ensure_elasticsearch_running


async def create_chatbot_graph():
    """Create and configure the chatbot graph (Hybrid RAG).

    Graph structure:
        process_input → retrieve → agent → [conditional] → tools → agent
                                                         ↓
                                                        end

    Features:
    - Always retrieves documents first (RAG)
    - Agent can use retrieved context
    - Agent can also call search_documents tool for additional searches

    Returns:
        Compiled StateGraph ready for execution
    """
    # Initialize LLM with tools (including search_documents for additional searches)
    tools = [get_weather, calculate, search_documents]
    # Use to_thread to avoid blocking event loop during heavy model loading
    chat_model: ChatOllama = await asyncio.to_thread(get_local_llm)
    # Ensure tool binding is correct for Qwen
    chat_model_with_tools = chat_model.bind_tools(tools)

    # Create graph
    workflow = StateGraph(ChatbotState)

    # Add nodes
    workflow.add_node("process_input", process_input)
    workflow.add_node("retrieve", retrieve_documents)
    workflow.add_node("agent", partial(call_model, llm_with_tools=chat_model_with_tools))
    workflow.add_node("tools", call_tools)

    # Configure edges - Hybrid RAG pattern
    workflow.set_entry_point("process_input")
    workflow.add_edge("process_input", "retrieve")
    workflow.add_edge("retrieve", "agent")
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
