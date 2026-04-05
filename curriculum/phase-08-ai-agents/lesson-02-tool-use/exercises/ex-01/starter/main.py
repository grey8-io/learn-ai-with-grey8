"""
Exercise: Tool Registry & Built-in Tools
============================================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py

Build a tool registry system with registration, execution,
error handling, and prompt formatting.
"""
import ast
import operator


# TODO: Implement calculator(expression)
#   - Takes an expression string like "2 + 3" or "10 * 5"
#   - Safely evaluate using ast.literal_eval for simple numeric expressions
#   - For expressions with operators, use this approach:
#     * Try ast.literal_eval(expression) first (handles plain numbers)
#     * If that fails, use eval() but ONLY if the expression contains
#       only digits, spaces, and the characters + - * / . ( )
#       Check with: all(c in '0123456789+-*/.() ' for c in expression)
#     * If the expression contains other characters, return an error
#   - Return the result as a string
#   - If any error occurs, return "Error: Could not evaluate '{expression}'."


# TODO: Implement word_count(text)
#   - Takes a text string
#   - Returns the number of words (split on whitespace) as a string
#   - Example: word_count("hello world") -> "2"


# TODO: Implement search_list(items, query)
#   - items: a list of strings
#   - query: a search string
#   - Return all items that contain the query (case-insensitive)
#   - Return as a string: "Found N results: item1, item2, ..."
#   - If no matches: "No results found for '{query}'."


# TODO: Build a `ToolRegistry` class with:
#
# __init__(self)
#   - Initialize self._tools as an empty dict (name -> tool info)
#
# register(self, name, fn, description, parameters=None)
#   - Store in self._tools[name]: {"fn": fn, "description": description, "parameters": parameters or {}}
#
# get_tool(self, name)
#   - Return the tool info dict for the given name
#   - Return None if not found
#
# list_tools(self)
#   - Return a list of dicts: [{"name": name, "description": description}, ...]
#   - One entry per registered tool
#
# format_tools_for_prompt(self)
#   - Return a formatted string listing all tools for an LLM prompt
#   - Format each tool as: "{i}. {name} — {description}"
#   - Number starting from 1
#   - Join with newlines
#   - Prefix with "Available tools:\n"
#   - Example output:
#     "Available tools:\n1. calculator — Evaluates math expressions.\n2. word_count — Counts words."
#
# execute(self, name, **kwargs)
#   - Look up the tool by name
#   - If not found, return "Error: Tool '{name}' not found."
#   - Call the tool's fn with **kwargs
#   - Return the result as a string
#   - If the function raises an exception, return "Error: {exception message}"


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
