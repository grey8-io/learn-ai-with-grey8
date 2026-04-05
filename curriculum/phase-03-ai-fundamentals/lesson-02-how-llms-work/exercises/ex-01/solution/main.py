"""
Exercise: Simple Tokenizer — Solution
=======================================
"""
import re


def simple_tokenize(text: str) -> list[str]:
    """Tokenize text into words and punctuation.

    Args:
        text: The input text to tokenize.

    Returns:
        A list of token strings.
    """
    return re.findall(r"\w+|[^\w\s]", text)


def count_tokens(text: str) -> int:
    """Count the number of tokens in a text.

    Args:
        text: The input text.

    Returns:
        The number of tokens.
    """
    return len(simple_tokenize(text))


def estimate_cost(text: str, price_per_1k: float) -> float:
    """Estimate the API cost for processing the given text.

    Args:
        text: The input text.
        price_per_1k: Price per 1,000 tokens.

    Returns:
        Estimated cost rounded to 6 decimal places.
    """
    token_count = count_tokens(text)
    cost = (token_count / 1000) * price_per_1k
    return round(cost, 6)


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    sample = "Hello, world! This is a simple tokenizer test."
    tokens = simple_tokenize(sample)
    print(f"Text: {sample}")
    print(f"Tokens: {tokens}")
    print(f"Token count: {count_tokens(sample)}")
    print(f"Estimated cost at $0.002/1K: ${estimate_cost(sample, 0.002)}")
