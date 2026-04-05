# Course Guide

The complete reference for the Learn AI With Grey8 curriculum. This is the single document you need throughout the course -- it covers how learning works, every lesson, every project, and all the dependencies you'll need.

---

## How the Learning Works

### Learning Cycle

Every lesson follows the same cycle:

```
Read Content  -->  Try Exercise  -->  Get Graded  -->  Take Quiz
     |                  |                 |               |
  content.md      starter/main.py    tests (60%)     quiz.json
                                   + AI rubric (40%)  (5 questions)
                        |
                   Need help?
                   3 progressive hints
                   + Socratic AI tutor chat
```

### What Each Component Does

| Component | What You Do | Format |
|-----------|------------|--------|
| **Content** | Read ~800-1000 words of lesson material with examples | Markdown (`content.md`) |
| **Exercise** | Write code in a starter file with TODO comments | Python (`starter/main.py`) |
| **Grading** | Submit your code and get a score | Automated tests (60%) + AI rubric (40%) |
| **Hints** | Request help when stuck (3 levels available) | JSON array (`hints.json`) |
| **Tutor** | Chat with a Socratic AI that asks guiding questions | Ollama-powered chat panel |
| **Quiz** | Answer multiple-choice questions to confirm understanding | JSON (`quiz.json`) — 5 (Phase 1-3), 7 (Phase 4-7), 10 (Phase 8-12) |

### Grading System

Exercises are graded on two axes:

| Component | Weight | How It Works |
|-----------|--------|-------------|
| **Automated tests** | 60% | Your code is run against pytest test cases |
| **AI rubric** | 40% | The local LLM evaluates your code against a rubric (code quality, approach, completeness) |

A combined score of **70% or higher** is considered passing.

### Hints System

Each exercise has 3 progressive hint levels. You can request hints one at a time:

| Level | Purpose | Example |
|-------|---------|---------|
| 1 -- Nudge | Points you in the right direction | "Start by creating a dictionary to store contacts" |
| 2 -- Approach | Describes the approach without giving code | "Use a while loop with input() to build an interactive menu" |
| 3 -- Near-solution | Gets you close to the answer | "The add function should append to the dict, the search should iterate and compare" |

### AI Tutor

The Socratic tutor is available via the chat panel on every lesson and exercise page (floating button on lessons, header button on exercises). It:

- Asks guiding questions instead of giving direct answers
- Has full context of the current lesson content, exercise TODOs, and your code
- Knows your personal profile -- level, streak, strengths, weaknesses -- and adapts accordingly
- On medium+ models (7B+), has cross-lesson awareness via the curriculum index
- Never gives you the complete solution
- Runs locally via Ollama -- no data leaves your machine
- Automatically detects your model's context window and adjusts how much context to include
- Chat history is saved per lesson and persists across sessions

### Gamification

The platform tracks your progress with a gamification system designed to build learning habits:

- **XP + Levels** -- earn XP from quizzes, exercises, and lesson completions. Level up from Beginner to AI Master across 7 ranks. 2x XP bonus when your streak is 3+ days
- **18 Achievement Badges** -- earn badges for milestones (First Blood, Full Stack), streaks (Streak Lord, Iron Will), skills (Perfect Score, No Hints Needed), and mastery (Phase Crusher, AI Master)
- **Streak Tracking** -- your daily learning streak is visualized with escalating fire icons and unlocks XP multipliers
- **Daily Goal** -- a circular progress ring encourages completing at least 1 lesson per day
- **Celebrations** -- confetti animations on lesson completion and level-up, plus toast notifications for XP and achievements

### Progress Tracking

All your progress is saved automatically:

- **Lesson completion** -- lessons are marked "in progress" when opened and auto-complete when you pass the quiz (Phase 1-3) or both the quiz and exercise at 70%+ (Phase 4-12). Already know the material? Skip straight to the quiz to prove it
- **Exercise submissions** -- every submission (code, score, feedback) is saved. Your best score is displayed, and your last code is restored when you return
- **Quiz results** -- your best attempt per quiz is recorded. Previous best score is shown when retaking
- **Chat history** -- tutor conversations are saved per lesson and restored when you reopen the chat

**Without signing in**, progress is stored in your browser's local storage. It persists across refreshes and restarts but is limited to one browser.

**With an account**, progress is stored in the database. This enables syncing across devices and multi-user tracking for teams and institutions.

> **Note:** You can start learning immediately without an account. If you create one later, your existing progress is automatically migrated.

---

## Curriculum Overview

The bootcamp is structured in **12 progressive phases** with **35 lessons**. Lessons are **strictly linear** -- each builds on the previous one. No prior programming experience is required.

### Phase-by-Phase Summary

| Phase | Focus | Lessons | Difficulty | Total Time | Key Concepts |
|-------|-------|---------|------------|------------|--------------|
| 1 | Dev Environment Setup | 3 | Easy | 2 hr 15 min | Terminal, Git, Python, VS Code, Ollama |
| 2 | Python Foundations | 3 | Easy-Medium | 2 hr 25 min | Variables, types, data structures, file I/O, HTTP |
| 3 | AI Fundamentals | 3 | Easy-Medium | 2 hr 10 min | ML concepts, LLM internals, tokenization, AI ethics |
| 4 | Your First AI App | 2 | Medium | 1 hr 35 min | Ollama API, multi-turn chat, CLI UX |
| 5 | Prompt Engineering | 3 | Medium | 2 hr 20 min | System prompts, personas, JSON output, few-shot, CoT |
| 6 | Embeddings & Search | 3 | Medium-Hard | 2 hr 30 min | Vector math, similarity, ChromaDB, semantic search |
| 7 | RAG Systems | 3 | Medium-Hard | 2 hr 40 min | Retrieval-augmented generation, chunking, document QA |
| 8 | AI Agents | 3 | Hard | 2 hr 35 min | ReAct pattern, tool use, function calling, multi-agent |
| 9 | AI Backend | 3 | Medium-Hard | 2 hr 35 min | FastAPI, async/await, production middleware |
| 10 | Optimization | 3 | Medium-Hard | 2 hr 25 min | Token counting, caching, batching, latency profiling |
| 11 | Deployment | 3 | Medium-Hard | 2 hr 35 min | Docker, cloud configs, monitoring, observability |
| 12 | Capstone | 3 | Medium-Hard | 2 hr 20 min | Architecture, testing strategies, portfolio showcase |

**Totals: 35 lessons | 35 exercises | 35 quizzes | ~27.7 hours**

### Difficulty Progression

```
Phase:  1    2    3    4    5    6    7    8    9   10   11   12
        ───────────  ───────────  ───────────  ───────────────
        Easy         Easy-Med     Medium       Med-Hard / Hard
```

| Difficulty | Count | Phases | What to Expect |
|-----------|-------|--------|----------------|
| Easy | 8 | 1-3 | Guided, foundational -- no prior programming needed |
| Medium | 14 | 2-6, 9-12 | Apply concepts, some problem-solving required |
| Hard | 13 | 6-12 | Design and build from scratch, multi-step problems |

Phases 1-3 assume no prior programming experience. By Phase 8, you are building autonomous AI agents.

---

## All 35 Lessons

### Phase 1 -- Dev Environment Setup

| ID | Lesson Title | Difficulty | Time | Exercise | Prerequisites |
|----|-------------|------------|------|----------|---------------|
| 01-01 | Terminal & Git Basics | Easy | 45 min | Your First Git Repository | None |
| 01-02 | Python Environment Setup | Easy | 40 min | Python Hello World with Functions | 01-01 |
| 01-03 | VS Code & AI Tools Setup | Easy | 50 min | Talk to a Local AI | 01-02 |

**What you learn:** Navigate the terminal, initialize Git repos, install Python, set up VS Code, and talk to a local LLM for the first time.

### Phase 2 -- Python Foundations

| ID | Lesson Title | Difficulty | Time | Exercise | Prerequisites |
|----|-------------|------------|------|----------|---------------|
| 02-01 | Variables, Types & Functions | Easy | 45 min | Temperature, Palindromes & BMI | 01-03 |
| 02-02 | Data Structures | Easy | 50 min | Contact Book | 02-01 |
| 02-03 | Working with Files & APIs | Medium | 50 min | Fetch and Save JSON | 02-02 |

**What you learn:** Python basics -- variables, functions, lists, dicts, file I/O, and making HTTP requests.

### Phase 3 -- AI Fundamentals

| ID | Lesson Title | Difficulty | Time | Exercise | Prerequisites |
|----|-------------|------------|------|----------|---------------|
| 03-01 | What is AI? ML Basics | Easy | 40 min | Classify ML Problems | 02-03 |
| 03-02 | How LLMs Work | Easy | 45 min | Simple Tokenizer | 03-01 |
| 03-03 | AI Limitations & Ethics | Medium | 45 min | AI Fact Checker | 03-02 |

**What you learn:** What machine learning is, how LLMs generate text (tokens, attention, inference), and understanding AI limitations and ethical considerations.

### Phase 4 -- Your First AI App

| ID | Lesson Title | Difficulty | Time | Exercise | Prerequisites |
|----|-------------|------------|------|----------|---------------|
| 04-01 | Calling LLM APIs | Medium | 50 min | OllamaChat Client | 03-03 |
| 04-02 | Building a CLI AI Assistant | Medium | 45 min | CLI Assistant Utilities | 04-01 |

**What you learn:** Call the Ollama API programmatically, handle responses, and build a multi-turn command-line chatbot.

### Phase 5 -- Prompt Engineering

| ID | Lesson Title | Difficulty | Time | Exercise | Prerequisites |
|----|-------------|------------|------|----------|---------------|
| 05-01 | Role Prompting & System Messages | Medium | 45 min | Prompt Engineering Utilities | 04-02 |
| 05-02 | Structured Outputs | Medium | 50 min | Output Parsers | 05-01 |
| 05-03 | Few-Shot & Chain of Thought | Medium | 45 min | Advanced Prompt Patterns | 05-02 |

**What you learn:** Craft effective prompts using system messages, personas, JSON output formatting, few-shot examples, and chain-of-thought reasoning.

### Phase 6 -- Embeddings & Search

| ID | Lesson Title | Difficulty | Time | Exercise | Prerequisites |
|----|-------------|------------|------|----------|---------------|
| 06-01 | What Are Embeddings? | Medium | 45 min | Embedding Utilities | 05-03 |
| 06-02 | Vector Databases | Medium | 50 min | Simple Vector Store | 06-01 |
| 06-03 | Building Semantic Search | Hard | 55 min | Semantic Search Engine | 06-02 |

**What you learn:** Convert text to vectors, measure similarity, store embeddings in ChromaDB, and build a search engine that understands meaning.

### Phase 7 -- RAG Systems

| ID | Lesson Title | Difficulty | Time | Exercise | Prerequisites |
|----|-------------|------------|------|----------|---------------|
| 07-01 | RAG Architecture | Medium | 50 min | RAG Pipeline | 06-03 |
| 07-02 | Document Chunking & Processing | Medium | 50 min | Document Chunking | 07-01 |
| 07-03 | Building a RAG Pipeline | Hard | 60 min | Document QA System | 07-02 |

**What you learn:** Retrieval-augmented generation -- chunk documents, embed and retrieve relevant context, and generate grounded answers.

### Phase 8 -- AI Agents

| ID | Lesson Title | Difficulty | Time | Exercise | Prerequisites |
|----|-------------|------------|------|----------|---------------|
| 08-01 | Agent Concepts & Patterns | Hard | 50 min | Simple Agent Framework | 07-03 |
| 08-02 | Tool Use & Function Calling | Hard | 50 min | Tool Registry System | 08-01 |
| 08-03 | Multi-Agent Systems | Hard | 55 min | Multi-Agent Orchestrator | 08-02 |

**What you learn:** Build AI agents that reason and act (ReAct), register and call tools, and coordinate multiple agents in a pipeline.

### Phase 9 -- AI Backend Development

| ID | Lesson Title | Difficulty | Time | Exercise | Prerequisites |
|----|-------------|------------|------|----------|---------------|
| 09-01 | FastAPI Basics | Medium | 50 min | AI-Ready API | 08-03 |
| 09-02 | Async AI Services | Hard | 55 min | Async LLM Client | 09-01 |
| 09-03 | Production Patterns | Hard | 50 min | Production Middleware | 09-02 |

**What you learn:** Build REST APIs with FastAPI, handle async LLM calls, and implement production patterns like rate limiting, retry logic, and structured logging.

### Phase 10 -- Optimization

| ID | Lesson Title | Difficulty | Time | Exercise | Prerequisites |
|----|-------------|------------|------|----------|---------------|
| 10-01 | Token & Cost Management | Medium | 45 min | Cost Tracker & Optimizer | 09-03 |
| 10-02 | Caching & Batching | Hard | 50 min | Intelligent Caching | 10-01 |
| 10-03 | Latency Optimization | Hard | 50 min | Performance Monitor | 10-02 |

**What you learn:** Count and budget tokens, implement semantic caching, batch API calls, and profile/optimize latency.

### Phase 11 -- Deployment

| ID | Lesson Title | Difficulty | Time | Exercise | Prerequisites |
|----|-------------|------------|------|----------|---------------|
| 11-01 | Docker Basics for AI Apps | Medium | 50 min | Docker Config Generator | 10-03 |
| 11-02 | Cloud Deployment | Hard | 50 min | Deployment Config Generator | 11-01 |
| 11-03 | Monitoring & Observability | Hard | 55 min | AI Monitoring System | 11-02 |

**What you learn:** Containerize AI apps with Docker, generate cloud deployment configs, and build monitoring dashboards with metrics and alerts.

### Phase 12 -- Capstone

| ID | Lesson Title | Difficulty | Time | Exercise | Prerequisites |
|----|-------------|------------|------|----------|---------------|
| 12-01 | Project Planning & Architecture | Medium | 45 min | Project Planner | 11-03 |
| 12-02 | Building & Testing AI Apps | Hard | 50 min | AI Test Harness | 12-01 |
| 12-03 | Deployment & Showcase | Medium | 45 min | Project Showcase Builder | 12-02 |

**What you learn:** Plan AI application architecture, write comprehensive test suites, and build a portfolio showcase for your projects.

---

## Capstone Projects

After completing the lessons, apply your skills to 15 real-world projects. Each project has a starter template in `projects/NN-project-name/starter/main.py` with TODO comments.

### All 15 Projects

| # | Project | Description | Key Libraries | Ollama Model | Applies Phases |
|---|---------|-------------|---------------|-------------|----------------|
| 01 | AI Chatbot | Multi-turn CLI chatbot with conversation history | `requests`, `rich` | llama3.2:3b | 1-4 |
| 02 | Document QA | Ingest PDFs into vectors, answer questions via RAG | `requests`, `chromadb`, `PyPDF2` | llama3.2:3b | 6-7 |
| 03 | Code Review Agent | Parse Python files and get structured review feedback | `requests`, `pathlib` | llama3.2:3b | 5, 8 |
| 04 | Semantic Search Engine | Embed documents and search by meaning via REST API | `requests`, `chromadb`, `flask` | llama3.2:3b | 6 |
| 05 | RAG Knowledge Base | Ingest Markdown notes, answer questions using RAG | `requests`, `chromadb`, `pathlib` | llama3.2:3b | 6-7 |
| 06 | Multi-Agent Pipeline | Chain Researcher/Writer/Reviewer agents for content | `requests` | llama3.2:3b | 8 |
| 07 | AI-Powered API | REST API with /summarize, /classify, /generate | `requests`, `fastapi`, `pydantic`, `uvicorn` | llama3.2:3b | 9 |
| 08 | Streaming Chat App | SSE streaming from Ollama with HTML chat client | `requests`, `fastapi`, `sse_starlette`, `uvicorn` | llama3.2:3b | 4, 9 |
| 09 | AI Content Moderator | Classify text as safe/warning/unsafe using LLM | `requests`, `fastapi`, `pydantic`, `uvicorn` | llama3.2:3b | 5, 9 |
| 10 | Local Copilot | Code completion endpoint via Flask + Ollama | `requests`, `flask` | llama3.2:3b | 5, 8 |
| 11 | AI Email Assistant | Generate professional emails from bullet points | `requests`, `rich` | llama3.2:3b | 4-5 |
| 12 | Image Description Service | Multimodal LLM describes uploaded images | `requests`, `fastapi`, `uvicorn` | **llava** | 9 |
| 13 | AI Testing Framework | Generate pytest tests from Python source code | `requests`, `pathlib` | llama3.2:3b | 5, 8 |
| 14 | Model Evaluation Dashboard | Compare models, track latency and quality metrics | `requests`, `pandas`, `streamlit` | llama3.2:3b | 10 |
| 15 | Full-Stack AI SaaS | Complete app: FastAPI backend with RAG + HTML frontend | `requests`, `fastapi`, `chromadb`, `Jinja2`, `uvicorn` | llama3.2:3b | 6-9, 11 |

> **Important:** Project 12 (Image Description Service) is the only project requiring the `llava` multimodal model. All other projects use `llama3.2:3b`. Pull it before starting that project: `ollama pull llava`

### Project Library Dependencies

All projects require `requests`. Here are the additional libraries you'll need:

| Library | Install Command | Used By Projects |
|---------|----------------|-----------------|
| `requests` | `pip install requests` | All 15 |
| `fastapi` | `pip install fastapi` | 07, 08, 09, 12, 15 |
| `uvicorn` | `pip install "uvicorn[standard]"` | 07, 08, 09, 12, 15 |
| `flask` | `pip install flask` | 04, 10 |
| `chromadb` | `pip install chromadb` | 02, 04, 05, 15 |
| `rich` | `pip install rich` | 01, 11 |
| `pydantic` | `pip install pydantic` | 07, 08, 09 |
| `sse-starlette` | `pip install sse-starlette` | 08 |
| `PyPDF2` | `pip install PyPDF2` | 02 |
| `streamlit` | `pip install streamlit` | 14 |
| `pandas` | `pip install pandas` | 14 |
| `Jinja2` | `pip install Jinja2` | 15 |

You do not need to install all libraries upfront. Install them as you start each project.

---

## Lesson File Structure

Every lesson lives under `curriculum/phase-NN-slug/lesson-NN-slug/` and contains:

```
lesson-NN-slug/
  content.md                          # Lesson text (~800-1000 words)
  quiz.json                           # Multiple-choice questions (5/7/10 by phase difficulty)
  exercises/
    ex-01/
      starter/main.py                 # Starter code with TODOs
      solution/main.py                # Complete working solution
      tests/test_exercise.py          # pytest tests for grading
      rubric.md                       # Grading criteria for AI evaluation
      hints.json                      # Array of exactly 3 progressive hints
```

---

## Common Commands

These commands work on all platforms (Windows, macOS, Linux). Run them from the project root directory.

```bash
# --- Start Services ---
ollama serve                                              # Start Ollama (skip on Windows if running in system tray)
cd tutor && uvicorn tutor.main:app --reload --port 8000   # Start tutor API
cd platform/web && npm run dev                            # Start web frontend
docker compose -f docker/docker-compose.yml up            # Or start everything via Docker

# --- Testing & Quality ---
cd tutor && pytest                  # Run tutor tests
cd platform/web && npm test         # Run web tests
cd ace && pytest                    # Run ACE tests
cd tutor && ruff check .            # Lint tutor code
cd platform/web && npm run lint     # Lint web code

# --- Documentation ---
npx docsify-cli serve docs --port 4000   # Serve docs locally at http://localhost:4000

# --- ACE Framework ---
ace sync                                       # Update manifest.json from curriculum files
ace generate --spec specs/phase-NN.yml         # Generate content from spec
ace curate --path curriculum/phase-NN/         # Validate + quality-check
ace reflect --output reports/                  # Curriculum analytics
```

> **Tip:** If you have `make` installed (standard on macOS/Linux; on Windows: `choco install make`), you can use shortcuts like `make dev`, `make test`, `make lint`, etc. Run `make help` to see all targets.
