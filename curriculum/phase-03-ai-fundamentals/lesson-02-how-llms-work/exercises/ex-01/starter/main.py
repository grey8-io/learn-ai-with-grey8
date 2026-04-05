"""
Exercise: Simple Tokenizer
============================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py

Build a simple word-level tokenizer that splits text into tokens
and estimates API costs.
"""
import re


# TODO 1: Write a function called `simple_tokenize` that:
#          - Takes one parameter: text (str)
#          - Splits the text into tokens (words and punctuation separately)
#          - Use re.findall(r"\w+|[^\w\s]", text) to split on words and punctuation
#          - Returns a list of token strings
#          - Example: "Hello, world!" -> ["Hello", ",", "world", "!"]


# TODO 2: Write a function called `count_tokens` that:
#          - Takes one parameter: text (str)
#          - Uses simple_tokenize() to tokenize the text
#          - Returns the number of tokens (int)


# TODO 3: Write a function called `estimate_cost` that:
#          - Takes two parameters: text (str) and price_per_1k (float)
#          - price_per_1k is the price per 1,000 tokens (e.g., 0.002)
#          - Uses count_tokens() to get the token count
#          - Returns the estimated cost as a float rounded to 6 decimal places
#          - Formula: cost = (token_count / 1000) * price_per_1k


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
