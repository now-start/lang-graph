"""AI Chatbot graph configuration.

This module defines the chatbot graph structure:
- Node connections
- Conditional edges
- State schema

Node implementations are in src/nodes/chatbot/
"""

from functools import partial
from langgraph.graph import StateGraph, END

from src.states import ChatbotState
from src.tools import get_weather, calculate
from src.utils import get_local_llm
from src.nodes import call_model, call_tools, should_continue


def create_chatbot_graph():
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
    chat_model = get_local_llm()
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


# Export function for LangGraph Dev (lazy initialization)
def graph():
    """Lazy graph initialization for LangGraph Dev."""
    return create_chatbot_graph()
