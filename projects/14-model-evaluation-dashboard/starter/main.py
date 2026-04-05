"""
Project 14: Model Evaluation Dashboard (Starter)
Compare model outputs, track latency and quality metrics via Streamlit.
"""

import time

import pandas as pd
import requests
import streamlit as st

# Ollama API configuration
OLLAMA_URL = "http://localhost:11434/api/chat"
MODEL = "llama3.2:3b"

# Default benchmark prompts
DEFAULT_PROMPTS = [
    "Explain what a Python list comprehension is in one sentence.",
    "Write a haiku about programming.",
    "What are three benefits of unit testing?",
    "Explain the difference between a stack and a queue.",
    "Summarize the concept of recursion for a beginner.",
]


def chat(prompt: str, model: str = MODEL) -> dict:
    """Send a prompt to Ollama and return response with timing metrics.

    Args:
        prompt: The user prompt to send.
        model: The model to use.

    Returns:
        A dict with keys: "response", "latency_ms", "response_length"
    """
    # TODO: Record the start time using time.time()
    #
    # TODO: Send a POST request to OLLAMA_URL with:
    #   - "model": model
    #   - "messages": [{"role": "user", "content": prompt}]
    #   - "stream": False
    #
    # TODO: Record the end time and calculate latency in milliseconds
    #
    # TODO: Extract the response text from the JSON
    #
    # TODO: Return a dict with:
    #   - "response": the text content
    #   - "latency_ms": round(latency in ms, 2)
    #   - "response_length": len(response text)
    pass


def run_benchmark(prompts: list[str], model: str = MODEL) -> pd.DataFrame:
    """Run all prompts through the model and collect metrics.

    Args:
        prompts: List of prompt strings to benchmark.
        model: The model to benchmark.

    Returns:
        A pandas DataFrame with columns:
        prompt, response, latency_ms, response_length
    """
    # TODO: Create an empty list to collect results
    #
    # TODO: Loop through each prompt:
    #   - Call chat() with the prompt and model
    #   - Add the prompt text to the result dict
    #   - Append to the results list
    #
    # TODO: Convert the results list to a DataFrame and return it
    #
    # Hint: pd.DataFrame(results) converts a list of dicts to a DataFrame
    pass


def display_results(df: pd.DataFrame):
    """Display benchmark results with charts and tables.

    Args:
        df: DataFrame with benchmark results.
    """
    # TODO: Display summary metrics using st.metric() in columns:
    #   - Average latency
    #   - Average response length
    #   - Total prompts run

    # TODO: Display a bar chart of latency per prompt
    # Hint: st.bar_chart() can take a DataFrame
    # You might want to create a chart-friendly DataFrame with prompt
    # numbers as index and latency_ms as values

    # TODO: Display a bar chart of response length per prompt

    # TODO: Display the full results table using st.dataframe()

    # TODO: Add a download button for CSV export
    # Hint: st.download_button() with df.to_csv()
    pass


def main():
    """Streamlit app entry point."""
    st.set_page_config(page_title="Model Evaluation Dashboard", layout="wide")
    st.title("Model Evaluation Dashboard")

    # TODO: Sidebar — Model configuration
    # Add a text input for the model name (default: MODEL)
    # Add a number input for how many prompts to run

    # TODO: Main area — Prompt editor
    # Use st.text_area() to let users edit the prompts (one per line)
    # Default to DEFAULT_PROMPTS joined by newlines
    # Parse the text back into a list of prompts

    # TODO: Run benchmark button
    # When clicked:
    #   - Show a spinner with st.spinner("Running benchmark...")
    #   - Call run_benchmark() with the prompts
    #   - Store results in st.session_state so they persist
    #   - Call display_results() to show the data

    # TODO: Show previous results if they exist in session_state

    pass


if __name__ == "__main__":
    main()
