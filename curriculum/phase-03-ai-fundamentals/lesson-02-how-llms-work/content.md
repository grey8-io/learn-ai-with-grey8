# How LLMs Work

Large Language Models like GPT, Llama, and Mistral are the engines behind modern AI assistants. In this lesson, you'll learn how they actually work — not at the PhD level, but enough to use them effectively and understand their strengths and weaknesses.

By the end of this lesson, you'll understand tokens, the transformer architecture, and the key parameters that control LLM behavior.

---

## Tokens: The Language of LLMs

LLMs don't read words the way humans do. They break text into **tokens** — small pieces that might be words, parts of words, or even individual characters.

For example, the sentence "Hello, world!" might be tokenized as:

```
["Hello", ",", " world", "!"]
```

Here's a more detailed look at how tokenization breaks down a sentence:

```
  "Hello, how are you?"
       ↓ tokenizer
  ["Hello", ",", " how", " are", " you", "?"]
    token1  t2    t3      t4      t5     t6

  6 tokens → model processes these, not characters
```

And a longer word like "unbelievable" might become:

```
["un", "believ", "able"]
```

### Why Tokens Matter

- **Cost**: API providers charge per token. More tokens = more money.
- **Context window**: Every LLM has a maximum number of tokens it can process at once (its "context window"). GPT-4 can handle ~128,000 tokens; smaller models might only handle 2,000-4,000.
- **Speed**: More tokens take longer to generate.

A rough rule of thumb: **1 token is approximately 4 characters** or about **3/4 of a word** in English. A 1,000-word article is roughly 1,300 tokens.

---

## The Transformer Architecture (High Level)

The **transformer** is the architecture that powers all modern LLMs. It was introduced in a 2017 paper called "Attention Is All You Need," and it revolutionized natural language processing.

Here's the key idea, explained simply:

### The Prediction Game

An LLM is fundamentally a **next-token predictor**. Given a sequence of tokens, it predicts the most likely next token. Then it adds that token to the sequence and predicts the next one, and so on.

```
  Input: "The capital of France is"
                    ↓
          ┌─────────────────┐
          │   LLM computes  │
          │   probabilities  │
          └────────┬────────┘
                   ↓
    "Paris" → 0.85  ←── most likely
    "Lyon"  → 0.04
    "a"     → 0.03
    "the"   → 0.02
    ...     → 0.06
```

When you type "The capital of France is", the model predicts that "Paris" is the most likely next token. It's not looking up facts — it's making a statistical prediction based on patterns it learned during training.

### Attention: The Secret Sauce

The transformer's breakthrough is the **attention mechanism**. It allows the model to look at all the other tokens in the input when predicting the next one, and to focus more on the relevant ones.

Think of reading a sentence: "The cat sat on the mat because **it** was tired." To understand what "it" refers to, you need to pay **attention** to "cat" earlier in the sentence. The attention mechanism does this automatically and at massive scale.

```
  "The cat sat on the mat because it was tired"
                                    │
                    ┌───────────────┘
                    ↓
              "it" attends to:
                "cat"  ████████░░  (strong)
                "mat"  ███░░░░░░░  (weak)
                "The"  █░░░░░░░░░  (minimal)
```

### Layers and Parameters

Transformers are built from stacked layers, each containing attention mechanisms and neural network components. A "large" language model has billions of **parameters** — numerical values that were adjusted during training.

- GPT-3: 175 billion parameters
- Llama 2: 7B to 70B parameters
- Mistral 7B: 7 billion parameters

More parameters generally means better performance, but also more memory and compute requirements. This is why running smaller models locally is practical, while the largest models require massive cloud infrastructure.

---

## Pre-training vs Fine-tuning

LLMs go through two main training phases:

### Pre-training

The model reads **enormous amounts of text** from the internet — books, articles, code, websites. It learns to predict the next token, and in doing so, it absorbs grammar, facts, reasoning patterns, and coding ability.

This phase is incredibly expensive. Training GPT-4 reportedly cost over $100 million. You'll never need to do this yourself.

### Fine-tuning

After pre-training, the model is further trained on **specific, curated data** to make it more useful. For example:

- **Instruction tuning**: Training on question-answer pairs so the model follows instructions
- **RLHF** (Reinforcement Learning from Human Feedback): Humans rate model outputs, and the model learns to produce responses that humans prefer

Fine-tuning is what turns a raw text predictor into a helpful assistant.

---

## Temperature and Sampling

When an LLM predicts the next token, it doesn't just pick one — it calculates probabilities for every possible token. The **temperature** parameter controls how it makes its choice:

- **Temperature 0**: Always picks the most probable token. Responses are deterministic and focused, but can be repetitive.
- **Temperature 0.7**: Introduces some randomness. Good balance of creativity and coherence.
- **Temperature 1.0+**: Very random. Creative but may produce nonsensical output.

Think of temperature like a creativity dial:

```
[0.0] Focused & Predictable ←————→ Creative & Surprising [1.5]
```

For factual tasks (code, math, data extraction), use low temperature. For creative tasks (writing, brainstorming), use higher temperature.

### Top-p (Nucleus Sampling)

Another parameter, **top-p**, controls the pool of tokens the model considers. A top-p of 0.9 means the model only considers tokens that make up the top 90% of probability mass, discarding very unlikely options.

---

## Context Windows

The **context window** is the maximum number of tokens an LLM can "see" at once — including both your input and the model's output.

If your conversation exceeds the context window, the model literally cannot see the beginning of the conversation anymore. It's like having a conversation through a window that only shows the last few paragraphs.

This is why:
- Long conversations can "forget" earlier context
- Sending an entire book in one prompt might not work
- Managing context is a key skill in AI development

---

## Putting It All Together

When you send a prompt to an LLM:

1. Your text is **tokenized** into tokens
2. The tokens are fed through the **transformer** layers
3. The model predicts the next token using **attention** and its learned **parameters**
4. **Temperature** and **top-p** control how the next token is selected
5. The selected token is added, and steps 2-4 repeat until the model generates a stop token or hits the **context window** limit

Understanding this process helps you write better prompts, debug unexpected behavior, and choose the right model for your task.

---

## Your Turn

In the exercise that follows, you'll build a simple tokenizer. While real tokenizers are far more sophisticated, building one from scratch will give you an intuitive feel for how text gets broken into tokens and how token counts relate to cost. Let's go!
