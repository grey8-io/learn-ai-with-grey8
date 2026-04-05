"""
Exercise: Structured Output Parsers — Solution
================================================
"""
import json
import re


def extract_json(text: str) -> dict | None:
    """Find and parse the first JSON object from a text string.

    Args:
        text: A string that may contain a JSON object somewhere in it.

    Returns:
        The parsed JSON as a dict, or None if no valid JSON is found.
    """
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            return None
    return None


def extract_markdown_sections(text: str) -> dict:
    """Parse markdown text into a dict of heading -> content.

    Args:
        text: Markdown-formatted text with headings.

    Returns:
        A dict mapping heading text to the content below that heading.
    """
    sections = {}
    current_heading = None
    current_content = []

    for line in text.split('\n'):
        if line.startswith('#'):
            if current_heading is not None:
                sections[current_heading] = '\n'.join(current_content).strip()
            current_heading = line.lstrip('#').strip()
            current_content = []
        else:
            current_content.append(line)

    if current_heading is not None:
        sections[current_heading] = '\n'.join(current_content).strip()

    return sections


def create_json_prompt(task: str, schema_description: str, example_output: str) -> str:
    """Create a prompt that instructs the LLM to return JSON.

    Args:
        task: Description of what the LLM should do.
        schema_description: Description of expected JSON fields.
        example_output: An example of the expected JSON output.

    Returns:
        A formatted prompt string.
    """
    return (
        f"{task}\n\n"
        f"Return your response as JSON with these fields:\n"
        f"{schema_description}\n\n"
        f"Example output:\n"
        f"{example_output}\n\n"
        f"Return ONLY valid JSON, no additional text."
    )


def validate_llm_json(text: str, required_fields: list[str]) -> dict:
    """Extract JSON from LLM text and validate required fields.

    Args:
        text: The raw LLM response text.
        required_fields: List of field names that must be present.

    Returns:
        A dict with valid, data, and missing_fields.
    """
    data = extract_json(text)
    if data is None:
        return {"valid": False, "data": None, "missing_fields": list(required_fields)}

    missing = [f for f in required_fields if f not in data]
    return {
        "valid": len(missing) == 0,
        "data": data,
        "missing_fields": missing,
    }


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
