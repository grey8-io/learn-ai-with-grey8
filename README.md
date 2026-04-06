# Learn AI With Grey8

A self-driving, open-source AI bootcamp powered by a local LLM tutor -- learn by building 15 real projects, zero cloud API keys required.

**12 phases | 35 lessons | 15 projects | ~28 hours | 100% local**

## Why This Exists

Most AI tutorials teach theory or require expensive cloud API keys. This bootcamp is different:

- **100% local** -- everything runs on your machine via Ollama, no API keys or cloud accounts needed
- **Learn by building** -- 35 hands-on exercises + 15 real projects, not just reading
- **AI-graded** -- every exercise is graded by real tests (60%) + AI rubric (40%)
- **Socratic AI tutor** -- a local LLM guides you with questions, not answers
- **Progressive** -- starts from "What is a terminal?" and ends with deploying full-stack AI apps
- **Progress tracking** -- submissions, quiz scores, and lesson completion saved automatically. Works without an account; sign in to sync across devices or for team tracking

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    learner's machine                    │
│                                                         │
│  ┌───────────┐   REST    ┌──────────────┐   Ollama     │
│  │  Next.js   │ <──────> │  FastAPI      │ <──────>    │
│  │  Web UI    │          │  Tutor Engine │   llama3.2   │
│  │  :3000     │          │  :8000        │   :11434     │
│  └─────┬─────┘          └──────┬───────┘              │
│        │                       │                       │
│        │       ┌───────────────┘                       │
│        v       v                                       │
│  ┌──────────────────┐                                  │
│  │    Supabase       │    ┌─────────────────┐          │
│  │    (local Docker) │    │  ACE Framework  │          │
│  │    :54321         │    │  generate /      │          │
│  │    Auth · DB ·    │    │  curate /        │          │
│  │    Storage        │    │  reflect         │          │
│  └──────────────────┘    └─────────────────┘          │
└─────────────────────────────────────────────────────────┘
```

## Quick Start

```bash
git clone https://github.com/grey8-io/learn-ai-with-grey8.git
cd learn-ai-with-grey8
bash scripts/setup.sh    # One-time setup: installs all dependencies, pulls AI model
bash scripts/start.sh    # Starts all services (Ollama, Tutor API, Web UI)
```

Open [http://localhost:3000](http://localhost:3000) to start learning.

For prerequisites and detailed instructions, see the **[Getting Started guide](docs/getting-started.md)**.

## Share This With Your Team

Know a developer who wants to learn AI? Send them this repo. No signup, no API keys, no subscriptions — they can start building in 5 minutes.

If you're a **team lead or engineering manager**, this is a free upskilling path for your developers. Share it in your team Slack, forward it to a colleague, or drop it in your engineering newsletter. The entire course runs locally — no corporate approvals needed.

> **Quick share link:** `https://github.com/grey8-io/learn-ai-with-grey8`

## Curriculum

<!-- CURRICULUM_TABLE_START -->
| Phase | Focus | Lessons | What You Build |
|-------|-------|---------|----------------|
| 1 | Dev Environment Setup | 3 | Terminal & Git Basics, Python Environment Setup, VS Code & AI Tools Setup |
| 2 | Python Foundations | 3 | Variables, Types & Functions, Data Structures, Working with Files & APIs |
| 3 | AI Fundamentals | 3 | What is AI? Machine Learning Basics, How LLMs Work, AI Limitations & Ethics |
| 4 | Your First AI App | 3 | Calling LLM APIs, Building a CLI AI Assistant, Milestone Project: AI Chatbot |
| 5 | Prompt Engineering | 3 | Role Prompting & System Messages, Structured Outputs, Few-Shot Patterns & Chain of Thought |
| 6 | Embeddings & Semantic Search | 3 | What Are Embeddings?, Vector Databases, Building Semantic Search |
| 7 | RAG Systems | 4 | RAG Architecture, Document Chunking & Processing, Building a RAG Pipeline, Milestone Project: RAG Knowledge Base |
| 8 | AI Agents | 3 | Agent Concepts & Patterns, Tool Use & Function Calling, Multi-Agent Systems |
| 9 | AI Backend Development | 4 | FastAPI Basics, Async AI Services, Production Patterns, Milestone Project: AI-Powered API |
| 10 | Optimization & Cost Control | 3 | Token & Cost Management, Caching & Batching, Latency Optimization |
| 11 | Deployment & Monitoring | 4 | Docker Basics for AI Apps, Cloud Deployment, Monitoring & Observability, Milestone Project: Streaming Chat App |
| 12 | Capstone Projects | 3 | Project Planning & Architecture, Building & Testing AI Applications, Deployment & Showcase |
<!-- CURRICULUM_TABLE_END -->

## Documentation

Browse the full course guide locally or on GitHub:

| Document | What It Covers |
|----------|---------------|
| **[Course Guide](docs/course-guide.md)** | Complete curriculum, all 35 lessons, 15 projects, learning cycle, library dependencies |
| **[Getting Started](docs/getting-started.md)** | Prerequisites, step-by-step setup, health checks, environment variables |
| **[Contributing](docs/contributing.md)** | Code style, adding content, PR process, project structure |

**Browse documentation:**

```bash
npx docsify-cli serve docs --port 4000   # Locally at http://localhost:4000
```

Or visit the hosted docs site (once GitHub Pages is enabled -- see below).

### Enabling GitHub Pages (one-time setup)

GitHub Pages serves the Docsify site directly from the `docs/` folder -- no build step, no CI needed.

1. Go to your repo on GitHub
2. Navigate to **Settings > Pages**
3. Under **Source**, select **Deploy from a branch**
4. Set branch to **`main`** and folder to **`/docs`**
5. Click **Save**

Your docs site will be live at `https://<your-username>.github.io/learn-ai-with-grey8/` within a few minutes. Every push to `main` updates the site automatically.

## Common Commands

```bash
# Start services (run each in a separate terminal)
ollama serve                                              # LLM runtime
cd tutor && uvicorn tutor.main:app --reload --port 8000   # Tutor API
cd platform/web && npm run dev                            # Web frontend

# Or start everything via Docker
docker compose -f docker/docker-compose.yml up

# Testing
cd tutor && pytest              # Tutor tests
cd platform/web && npm test     # Web tests
cd ace && pytest                # ACE tests

# Linting
cd tutor && ruff check .        # Python lint
cd platform/web && npm run lint # TypeScript lint

# Documentation
npx docsify-cli serve docs --port 4000   # Serve docs locally
```

> **Tip:** If you have `make` installed (standard on macOS/Linux; on Windows: `choco install make`), you can use shortcuts like `make dev`, `make test`, `make lint`. Run `make help` for all targets.

## Community

- **Star this repo** to bookmark it and help others discover it
- **Follow [Nagaraju Mudunuri](https://www.linkedin.com/in/nagaraju-mudunuri-42a05b25/) on LinkedIn** for AI career tips and course updates

## Contributing

We welcome contributions of all kinds -- curriculum content, platform features, bug fixes, and translations.

Please read [docs/contributing.md](docs/contributing.md) before opening a PR.

## License

This project is licensed under the [GNU Affero General Public License v3.0 (AGPL-3.0)](LICENSE).

You are free to use, modify, and distribute this software. If you run a modified version as a network service, you must make your source code available under the same license. The "Grey8" name and branding are trademarks and may not be used in derivative works without permission.
