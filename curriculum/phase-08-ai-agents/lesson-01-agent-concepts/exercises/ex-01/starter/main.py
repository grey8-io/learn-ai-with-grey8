"""
Exercise: Simple Agent Framework
====================================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py

Build a basic AI agent with tools, action parsing, and an agent loop.
"""
import re


# TODO: Build a `Tool` class with:
#   __init__(self, name, description, function)
#     - name: str — the tool's name
#     - description: str — what the tool does
#     - function: callable — the function to execute


# TODO: Build an `AgentState` class with:
#   __init__(self)
#     - messages: list — starts as empty list
#     - tool_results: list — starts as empty list
#     - iteration: int — starts at 0


# TODO: Build a `SimpleAgent` class with:
#
# __init__(self, tools, generate_fn, max_iterations=5)
#   - tools: a list of Tool objects
#   - generate_fn: callable that takes (str) -> str (a prompt in, response out)
#   - max_iterations: int — safety limit for the agent loop
#   - Store all as instance attributes
#
# parse_action(self, response)
#   - Parse the LLM response for the pattern: ACTION: tool_name(args)
#   - Use regex: r'ACTION:\s*(\w+)\((.+?)\)' to find tool calls
#   - If found, return {"tool": tool_name, "args": args_string}
#   - If not found, return None (means the response is a final answer)
#
# execute_tool(self, tool_name, args)
#   - Find the tool with matching name in self.tools
#   - Call tool.function(args) and return the result as a string
#   - If tool not found, return "Error: Tool '{tool_name}' not found."
#
# run(self, query)
#   - Create an AgentState
#   - Add the query to state.messages as {"role": "user", "content": query}
#   - Loop up to self.max_iterations times:
#     1. Build prompt from state.messages (join all message contents with newlines)
#     2. Call self.generate_fn(prompt) to get the LLM response
#     3. Add response to state.messages as {"role": "assistant", "content": response}
#     4. Call self.parse_action(response)
#     5. If no action (None), return {"answer": response, "iterations": state.iteration}
#     6. If action found:
#        - Call self.execute_tool(action["tool"], action["args"])
#        - Add tool result to state.messages as {"role": "tool", "content": result}
#        - Add result to state.tool_results
#        - Increment state.iteration
#   - If max iterations reached, return {"answer": "Max iterations reached.", "iterations": state.iteration}


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    # Define some tools
    calc_tool = Tool(
        name="calculator",
        description="Evaluates a math expression",
        function=lambda expr: str(eval(expr)),
    )

    # Track call count for demo
    call_count = 0

    def mock_generate(prompt):
        global call_count
        call_count += 1
        if call_count == 1:
            return "I need to calculate this. ACTION: calculator(2 + 3)"
        return "The answer is 5."

    agent = SimpleAgent(
        tools=[calc_tool],
        generate_fn=mock_generate,
        max_iterations=5,
    )

    result = agent.run("What is 2 + 3?")
    print(f"Answer: {result['answer']}")
    print(f"Iterations: {result['iterations']}")
