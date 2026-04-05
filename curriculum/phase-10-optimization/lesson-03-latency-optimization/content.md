# Latency Optimization

Users don't wait. Studies show that after 3 seconds, 50% of users abandon a request. AI applications routinely take 5-30 seconds to respond. That's a problem. In this lesson, you'll learn where latency comes from in AI systems, how to measure it, and practical techniques to make your applications feel fast -- even when the underlying models are slow.

---

## Where Does Latency Come From?

An AI request passes through several stages, each adding time:

| Stage | Typical Latency | Can Optimize? |
|---|---|---|
| Network (client to server) | 10-100ms | CDN, edge servers |
| Input preprocessing | 1-50ms | Faster parsing |
| Model inference (the big one) | 500-15,000ms | Model choice, quantization |
| Output postprocessing | 1-50ms | Simpler formatting |
| Network (server to client) | 10-100ms | Compression, streaming |

Model inference dominates. A GPT-4-class model might take 10 seconds to generate a full response. A smaller model might take 1 second. The right model for the task is often the biggest optimization.

```
  Total request time: 2.5 seconds

  ┌────────┬───────────────────────────────┬──────┐
  │Network │        LLM Inference          │Parse │
  │ 50ms   │         2300ms                │150ms │
  └────────┴───────────────────────────────┴──────┘

  92% of time is LLM inference — optimize there first!
```

---

## Measurement First

You can't optimize what you don't measure. A latency tracker records timing data for every operation:

```python
import time

class LatencyTracker:
    def __init__(self):
        self.operations = {}  # name -> list of durations in ms
        self.pending = {}     # name -> start time

    def start(self, operation_name):
        self.pending[operation_name] = time.time()

    def end(self, operation_name):
        if operation_name in self.pending:
            duration_ms = (time.time() - self.pending[operation_name]) * 1000
            if operation_name not in self.operations:
                self.operations[operation_name] = []
            self.operations[operation_name].append(duration_ms)
            del self.pending[operation_name]
```

### Percentile Statistics

Averages lie. If 99 requests take 100ms and 1 takes 10 seconds, the average is 199ms -- which represents nobody's actual experience. Use percentiles instead:

- **p50 (median)**: Half of requests are faster than this
- **p95**: 95% of requests are faster -- the "typical worst case"
- **p99**: 99% of requests are faster -- catches outliers

```python
def percentile(data, p):
    sorted_data = sorted(data)
    index = int(len(sorted_data) * p / 100)
    index = min(index, len(sorted_data) - 1)
    return sorted_data[index]
```

When someone says "our p95 is 2 seconds," they mean 95% of users get a response in under 2 seconds.

---

## Streaming: Perceived vs Actual Latency

The most effective latency optimization for AI is **streaming**. Instead of waiting for the complete response, send tokens as they're generated:

**Without streaming**: User waits 5 seconds, then sees the complete response.
**With streaming**: User sees the first word in 200ms, and the rest flows in over 5 seconds.

The total time is the same, but the *perceived* latency drops from 5 seconds to 200ms. Users feel like the system is responsive because they see progress immediately.

```
  Buffered:
  User waits... ░░░░░░░░░░░░░░░░ "Full response appears"
  Perceived:    |←── 3 seconds ──→|

  Streaming:
  User sees...  "The" "cat" "sat" "on" "the" "mat" ...
  Perceived:    |← 0.2s →| (first token!)

  Same total time, but streaming FEELS instant
```

### Stream Buffering

Raw token streaming can be jittery -- sometimes you get single characters, sometimes nothing for 500ms. A buffer smooths this out:

```python
class StreamBuffer:
    def __init__(self, min_chars=10):
        self.min_chars = min_chars
        self.buffer = ""

    def add(self, chunk):
        self.buffer += chunk
        if len(self.buffer) >= self.min_chars:
            output = self.buffer
            self.buffer = ""
            return output
        return ""

    def flush(self):
        output = self.buffer
        self.buffer = ""
        return output
```

The buffer accumulates small chunks and only emits when there's enough text for a smooth display. Call `flush()` at the end to get any remaining content.

---

## Parallel Processing

When a request requires multiple independent operations, run them in parallel:

```python
import asyncio

# Sequential: 3 seconds total
result1 = await call_model_a(prompt)  # 1 second
result2 = await call_model_b(prompt)  # 1 second
result3 = await embed(prompt)         # 1 second

# Parallel: 1 second total (limited by the slowest)
result1, result2, result3 = await asyncio.gather(
    call_model_a(prompt),
    call_model_b(prompt),
    embed(prompt),
)
```

Common parallel patterns in AI apps:
- Generate response + log analytics simultaneously
- Fetch context from multiple sources before prompting
- Run safety checks in parallel with main inference

---

## Model Quantization Concepts

Quantization reduces model precision (e.g., 32-bit to 4-bit), making models smaller and faster:

| Precision | Memory | Speed | Quality |
|---|---|---|---|
| FP32 (full) | 100% | Baseline | Best |
| FP16 (half) | 50% | ~2x faster | 99% of full |
| INT8 | 25% | ~3x faster | 97% of full |
| INT4 | 12.5% | ~4x faster | 90-95% of full |

In Ollama, you often see model names like `llama3:7b-q4_0` -- the `q4` means 4-bit quantization. It runs much faster with slightly lower quality.

---

## Local vs Remote Tradeoffs

| Factor | Local (Ollama) | Remote (API) |
|---|---|---|
| Latency | Low (no network) | Higher (network round-trip) |
| Cost | Hardware only | Per-token pricing |
| Model size | Limited by RAM/VRAM | Any size available |
| Privacy | Data stays local | Data sent to provider |
| Scaling | Limited by hardware | Scales elastically |

For development and privacy-sensitive applications, local models win on latency. For production at scale, remote APIs are often more practical.

---

## Estimating Generation Time

A rough estimate helps set user expectations:

```python
def estimate_time(input_length, model_speed_tokens_per_sec=30):
    output_tokens = input_length // 4  # Rough estimate
    return output_tokens / model_speed_tokens_per_sec
```

Typical speeds:
- Fast local model (7B quantized): 30-50 tokens/sec
- Large local model (70B): 5-15 tokens/sec
- Cloud API (GPT-4): 20-40 tokens/sec
- Cloud API (GPT-3.5): 60-100 tokens/sec

---

## What You'll Build

In the exercise, you'll create a `LatencyTracker` with percentile statistics, a timing decorator, a `StreamBuffer` for smooth streaming, and a time estimation utility. These tools help you measure, understand, and improve the performance of any AI application.

Let's make your AI feel fast.
