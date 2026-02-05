"""Tool execution node."""

import asyncio
from langchain_core.messages import ToolMessage

from src.states import ChatbotState
from src.tools import get_weather, calculate


async def call_tools(state: ChatbotState) -> ChatbotState:
    """Execute tool calls from LLM response.

    Args:
        state: Current chatbot state with message history

    Returns:
        Updated state with tool execution results
    """
    messages = state["messages"]
    last_message = messages[-1]

    tool_results = []
    for tool_call in last_message.tool_calls:
        # Find and execute the tool
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]

        if tool_name == "get_weather":
            # Run in thread since tools may have blocking operations
            result = await asyncio.to_thread(get_weather.invoke, tool_args)
        elif tool_name == "calculate":
            result = await asyncio.to_thread(calculate.invoke, tool_args)
        else:
            result = f"Unknown tool: {tool_name}"

        tool_results.append(
            ToolMessage(
                content=result,
                tool_call_id=tool_call["id"]
            )
        )

    return {"messages": tool_results}
