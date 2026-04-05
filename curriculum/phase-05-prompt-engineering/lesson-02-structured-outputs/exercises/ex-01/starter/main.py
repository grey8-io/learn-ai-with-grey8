"""
Exercise: Structured Output Parsers
=====================================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py

Build utility functions for parsing and validating structured LLM outputs.
"""
import json
import re


def extract_json(text: str) -> dict | None:
    """Find and parse the first JSON object from a text string.

    LLMs often wrap JSON in extra text like "Here's the result:" or
    "Hope that helps!". This function extracts just the JSON part.

    Args:
        text: A string that may contain a JSON object somewhere in it.

    Returns:
        The parsed JSON as a dict, or None if no valid JSON is found.
    """
    # TODO: Implement this function.
    # 1. Use re.search with the pattern r'\{.*\}' and re.DOTALL flag
    #    to find content between the first { and last }.
    # 2. If a match is found, try json.loads(match.group()).
    # 3. Return the parsed dict, or None if no match or invalid JSON.
    pass


def extract_markdown_sections(text: str) -> dict:
    """Parse markdown text into a dict of heading -> content.

    Handles headings at any level (# , ## , ### , etc.).

    Args:
        text: Markdown-formatted text with headings.

    Returns:
        A dict mapping heading text (without # symbols) to the content
        below that heading (as a stripped string).
    """
    # TODO: Implement this function.
    # 1. Initialize an empty dict, current_heading = None, current_content = [].
    # 2. Loop through lines of text.
    # 3. If a line starts with '# ' (one or more # followed by space):
    #    - Save previous heading's content if current_heading is not None.
    #    - Set current_heading to the line with '#' symbols stripped.
    #    - Reset current_content to [].
    # 4. Otherwise, append the line to current_content.
    # 5. After the loop, save the last heading's content.
    # 6. Return the dict.
    pass


def create_json_prompt(task: str, schema_description: str, example_output: str) -> str:
    """Create a prompt that instructs the LLM to return JSON.

    Args:
        task: Description of what the LLM should do.
        schema_description: Description of expected JSON fields.
        example_output: An example of the expected JSON output.

    Returns:
        A formatted prompt string.

    Format:
        {task}

        Return your response as JSON with these fields:
        {schema_description}

        Example output:
        {example_output}

        Return ONLY valid JSON, no additional text.
    """
    # TODO: Implement this function.
    # Assemble the prompt string following the format above.
    pass


def validate_llm_json(text: str, required_fields: list[str]) -> dict:
    """Extract JSON from LLM text and validate required fields.

    Args:
        text: The raw LLM response text.
        required_fields: List of field names that must be present.

    Returns:
        A dict with:
            - valid (bool): True if JSON was extracted and has all required fields.
            - data (dict | None): The parsed JSON data, or None if extraction failed.
            - missing_fields (list[str]): List of required fields not found in the data.
    """
    # TODO: Implement this function.
    # 1. Call extract_json(text) to get the data.
    # 2. If data is None, return {valid: False, data: None, missing_fields: required_fields}.
    # 3. Find which required_fields are missing from the data's keys.
    # 4. Return {valid: len(missing)==0, data: data, missing_fields: missing}.
    pass


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    sample = """Here's the extracted info:
    {"name": "Widget", "price": 9.99, "in_stock": true}
    Hope that helps!"""

    result = extract_json(sample)
    print(f"Extracted JSON: {result}")

    md = """# Summary
This code looks good overall.

# Issues
- Missing error handling
- No type hints

# Suggestions
Add try/except blocks."""
    sections = extract_markdown_sections(md)
    print(f"Sections: {sections}")

    prompt = create_json_prompt(
        "Extract product info",
        "name (string), price (number)",
        '{"name": "Example", "price": 0.00}',
    )
    print(f"Prompt:\n{prompt}")

    validation = validate_llm_json(sample, ["name", "price"])
    print(f"Validation: {validation}")
