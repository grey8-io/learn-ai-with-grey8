"""
Project 14: Model Evaluation Dashboard (Reference)
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
    """Send a prompt to Ollama and return response with timing metrics."""
    start = time.time()

    response = requests.post(
        OLLAMA_URL,
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "stream": False,
        },
    )
    response.raise_for_status()

    latency_ms = round((time.time() - start) * 1000, 2)
    content = response.json()["message"]["content"]

    return {
        "response": content,
        "latency_ms": latency_ms,
        "response_length": len(content),
    }


def run_benchmark(prompts: list[str], model: str = MODEL) -> pd.DataFrame:
    """Run all prompts through the model and collect metrics."""
    results = []
    for prompt in prompts:
        result = chat(prompt, model)
        result["prompt"] = prompt
        results.append(result)
    return pd.DataFrame(results)


def display_results(df: pd.DataFrame):
    """Display benchmark results with charts and tables."""
    # Summary metrics row
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Avg Latency", f"{df['latency_ms'].mean():.0f} ms")
    with col2:
        st.metric("Avg Response Length", f"{df['response_length'].mean():.0f} chars")
    with col3:
        st.metric("Prompts Run", len(df))

    st.divider()

    # Charts side by side
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Latency per Prompt (ms)")
        chart_df = pd.DataFrame(
            {"Latency (ms)": df["latency_ms"].values},
            index=[f"P{i+1}" for i in range(len(df))],
        )
        st.bar_chart(chart_df)

    with chart_col2:
        st.subheader("Response Length per Prompt")
        chart_df = pd.DataFrame(
            {"Length (chars)": df["response_length"].values},
            index=[f"P{i+1}" for i in range(len(df))],
        )
        st.bar_chart(chart_df)

    st.divider()

    # Detailed results
    st.subheader("Detailed Results")
    for i, row in df.iterrows():
        with st.expander(f"P{i+1}: {row['prompt'][:60]}..."):
            st.write(f"**Latency:** {row['latency_ms']} ms")
            st.write(f"**Length:** {row['response_length']} chars")
            st.markdown(row["response"])

    # Full table
    st.subheader("Raw Data")
    st.dataframe(df[["prompt", "latency_ms", "response_length"]], use_container_width=True)

    # CSV export
    csv = df.to_csv(index=False)
    st.download_button("Download CSV", csv, "benchmark_results.csv", "text/csv")


def main():
    """Streamlit app entry point."""
    st.set_page_config(page_title="Model Evaluation Dashboard", layout="wide")
    st.title("Model Evaluation Dashboard")

    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")
        model = st.text_input("Model", value=MODEL)
        st.divider()
        st.markdown("**How it works:**")
        st.markdown(
            "1. Edit prompts in the main area\n"
            "2. Click 'Run Benchmark'\n"
            "3. View latency and quality metrics"
        )

    # Prompt editor
    st.subheader("Test Prompts")
    prompt_text = st.text_area(
        "Enter prompts (one per line):",
        value="\n".join(DEFAULT_PROMPTS),
        height=200,
    )
    prompts = [p.strip() for p in prompt_text.strip().split("\n") if p.strip()]
    st.caption(f"{len(prompts)} prompts ready")

    # Run benchmark
    if st.button("Run Benchmark", type="primary"):
        if not prompts:
            st.error("Add at least one prompt.")
            return

        progress = st.progress(0, text="Running benchmark...")
        results = []
        for i, prompt in enumerate(prompts):
            result = chat(prompt, model)
            result["prompt"] = prompt
            results.append(result)
            progress.progress((i + 1) / len(prompts), text=f"Prompt {i+1}/{len(prompts)}...")

        progress.empty()
        st.session_state["results"] = pd.DataFrame(results)

    # Display results if available
    if "results" in st.session_state:
        st.divider()
        display_results(st.session_state["results"])


if __name__ == "__main__":
    main()
