"""Calculator tool."""

from langchain_core.tools import tool


@tool
def calculate(expression: str) -> str:
    """Evaluate a mathematical expression.

    Args:
        expression: A mathematical expression to evaluate (e.g., "2 + 2")
    """
    try:
        # Safe evaluation with restricted builtins
        result = eval(expression, {"__builtins__": {}})
        return str(result)
    except Exception as e:
        return f"Error calculating: {str(e)}"
