"""
Exercise: Tool Registry & Built-in Tools — Solution
======================================================
"""
import ast
import operator


def calculator(expression: str) -> str:
    """Safely evaluate a math expression.

    Args:
        expression: A math expression string like "2 + 3".

    Returns:
        The result as a string, or an error message.
    """
    try:
        # Try simple literal eval first (handles plain numbers)
        return str(ast.literal_eval(expression))
    except (ValueError, SyntaxError):
        pass

    # Only allow safe characters
    if not all(c in "0123456789+-*/.() " for c in expression):
        return f"Error: Could not evaluate '{expression}'."

    try:
        result = eval(expression)
        return str(result)
    except Exception:
        return f"Error: Could not evaluate '{expression}'."


def word_count(text: str) -> str:
    """Count the number of words in text.

    Args:
        text: The input text.

    Returns:
        The word count as a string.
    """
    return str(len(text.split()))


def search_list(items: list[str], query: str) -> str:
    """Search a list of strings for items matching a query.

    Args:
        items: A list of strings to search.
        query: The search query.

    Returns:
        A formatted string with results.
    """
    query_lower = query.lower()
    matches = [item for item in items if query_lower in item.lower()]
    if not matches:
        return f"No results found for '{query}'."
    return f"Found {len(matches)} results: {', '.join(matches)}"


class ToolRegistry:
    """A registry for managing and executing tools."""

    def __init__(self):
        """Initialize the tool registry."""
        self._tools: dict = {}

    def register(
        self, name: str, fn, description: str, parameters: dict | None = None
    ):
        """Register a tool.

        Args:
            name: The tool's name.
            fn: The callable function.
            description: What the tool does.
            parameters: Optional parameter descriptions.
        """
        self._tools[name] = {
            "fn": fn,
            "description": description,
            "parameters": parameters or {},
        }

    def get_tool(self, name: str) -> dict | None:
        """Get tool info by name.

        Args:
            name: The tool name.

        Returns:
            The tool info dict, or None if not found.
        """
        return self._tools.get(name)

    def list_tools(self) -> list[dict]:
        """List all registered tools.

        Returns:
            A list of dicts with name and description.
        """
        return [
            {"name": name, "description": info["description"]}
            for name, info in self._tools.items()
        ]

    def format_tools_for_prompt(self) -> str:
        """Format all tools as a text block for an LLM prompt.

        Returns:
            A formatted string listing all tools.
        """
        lines = ["Available tools:"]
        for i, (name, info) in enumerate(self._tools.items(), 1):
            lines.append(f"{i}. {name} — {info['description']}")
        return "\n".join(lines)

    def execute(self, name: str, **kwargs) -> str:
        """Execute a tool by name.

        Args:
            name: The tool name.
            **kwargs: Arguments to pass to the tool function.

        Returns:
            The tool's result as a string, or an error message.
        """
        tool = self._tools.get(name)
        if tool is None:
            return f"Error: Tool '{name}' not found."
        try:
            result = tool["fn"](**kwargs)
            return str(result)
        except Exception as e:
            return f"Error: {str(e)}"


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    registry = ToolRegistry()
    registry.register(
        "calculator", calculator,
        "Evaluates a math expression and returns the result.",
        {"expression": "A math expression string"},
    )
    registry.register(
        "word_count", word_count,
        "Counts the number of words in text.",
        {"text": "The text to count words in"},
    )

    print(registry.format_tools_for_prompt())
    print()
    print(f"calculator: {registry.execute('calculator', expression='2 + 3')}")
    print(f"word_count: {registry.execute('word_count', text='hello world foo')}")

    items = ["Python tutorial", "Java guide", "Python cookbook", "Rust handbook"]
    print(f"search: {search_list(items, 'python')}")
