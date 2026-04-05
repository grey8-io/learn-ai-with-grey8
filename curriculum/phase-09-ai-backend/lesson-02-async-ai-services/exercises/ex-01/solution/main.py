"""
Exercise: Async AI Service Utilities — Solution
==================================================
"""

import asyncio
import httpx


class AsyncLLMClient:
    """Async client for communicating with an LLM API."""

    def __init__(self, base_url: str, timeout: float = 30.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    async def generate(self, prompt: str, model: str = "default") -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/generate",
                json={"model": model, "prompt": prompt},
                timeout=self.timeout,
            )
            return response.json()["response"]

    async def generate_stream(self, prompt: str, model: str = "default"):
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{self.base_url}/api/generate",
                json={"model": model, "prompt": prompt, "stream": True},
                timeout=self.timeout,
            ) as response:
                async for line in response.aiter_lines():
                    yield line

    async def batch_generate(
        self, prompts: list[str], model: str = "default", max_concurrent: int = 3
    ) -> list[str]:
        semaphore = asyncio.Semaphore(max_concurrent)

        async def _limited_generate(prompt: str) -> str:
            async with semaphore:
                return await self.generate(prompt, model)

        results = await asyncio.gather(*[_limited_generate(p) for p in prompts])
        return list(results)


async def retry_with_backoff(fn, max_retries: int = 3, base_delay: float = 1.0):
    """Retry an async function with exponential backoff."""
    for attempt in range(max_retries):
        try:
            return await fn()
        except Exception:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)
            await asyncio.sleep(delay)


def create_sse_response(chunks: list[str]) -> list[str]:
    """Convert a list of text chunks into SSE-formatted strings."""
    return [f"data: {chunk}\n\n" for chunk in chunks]


# ---------------------------------------------------------------------------
# Do not modify below this line
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("SSE example:")
    sse = create_sse_response(["Hello", " world", "!"])
    for msg in sse:
        print(repr(msg))
