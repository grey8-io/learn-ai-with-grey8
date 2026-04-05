"""
Exercise: Async AI Service Utilities
=======================================
Complete the TODOs below.  When you're finished, run the tests:

    pytest ../tests/test_exercise.py

Build async utilities for AI backends.
"""

import asyncio
import httpx


class AsyncLLMClient:
    """Async client for communicating with an LLM API.

    Attributes:
        base_url: The base URL of the LLM API (e.g., "http://localhost:11434").
        timeout: Request timeout in seconds.
    """

    def __init__(self, base_url: str, timeout: float = 30.0):
        """Initialize the client.

        Args:
            base_url: Base URL of the LLM API.
            timeout: Request timeout in seconds (default 30.0).
        """
        # TODO: Store base_url (strip trailing slash) and timeout.
        pass

    async def generate(self, prompt: str, model: str = "default") -> str:
        """Send a prompt to the LLM and return the response.

        Makes an async POST request to {base_url}/api/generate with JSON body:
            {"model": model, "prompt": prompt}

        Returns the "response" field from the JSON response.
        Uses self.timeout for the request timeout.
        """
        # TODO: Use httpx.AsyncClient to POST to {self.base_url}/api/generate
        # with json={"model": model, "prompt": prompt} and timeout=self.timeout.
        # Return response.json()["response"].
        pass

    async def generate_stream(self, prompt: str, model: str = "default"):
        """Stream a response from the LLM as an async generator.

        Makes an async POST request to {base_url}/api/generate with JSON body:
            {"model": model, "prompt": prompt, "stream": True}

        Yields each line from the streaming response.
        """
        # TODO: Use httpx.AsyncClient with client.stream("POST", ...) to
        # stream the response. Use async for line in response.aiter_lines()
        # to yield each line.
        pass

    async def batch_generate(
        self, prompts: list[str], model: str = "default", max_concurrent: int = 3
    ) -> list[str]:
        """Process multiple prompts concurrently with a concurrency limit.

        Uses an asyncio.Semaphore to limit concurrent requests to max_concurrent.
        Returns results in the same order as the input prompts.
        """
        # TODO:
        # 1. Create an asyncio.Semaphore(max_concurrent).
        # 2. Define an inner async function that acquires the semaphore
        #    and calls self.generate(prompt, model).
        # 3. Use asyncio.gather() to run all prompts concurrently.
        # 4. Return the list of results.
        pass


async def retry_with_backoff(fn, max_retries: int = 3, base_delay: float = 1.0):
    """Retry an async function with exponential backoff.

    Args:
        fn: An async callable (no arguments) to retry.
        max_retries: Maximum number of attempts (default 3).
        base_delay: Base delay in seconds (default 1.0).
            Delay doubles each retry: base_delay, base_delay*2, base_delay*4, ...

    Returns:
        The result of fn() on success.

    Raises:
        The last exception if all retries fail.
    """
    # TODO:
    # 1. Loop from 0 to max_retries - 1.
    # 2. Try to return await fn().
    # 3. On exception, if it's the last attempt, raise.
    # 4. Otherwise, sleep for base_delay * (2 ** attempt).
    pass


def create_sse_response(chunks: list[str]) -> list[str]:
    """Convert a list of text chunks into SSE-formatted strings.

    Each chunk becomes "data: {chunk}\\n\\n".

    Args:
        chunks: List of text chunks.

    Returns:
        List of SSE-formatted strings.
    """
    # TODO: Return a list where each chunk is formatted as "data: {chunk}\n\n".
    pass


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("SSE example:")
    sse = create_sse_response(["Hello", " world", "!"])
    for msg in sse:
        print(repr(msg))
