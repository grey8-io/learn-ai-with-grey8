# Learn AI With Grey8

> A self-driving, open-source AI bootcamp powered by a local LLM tutor -- learn by building 15 real projects, zero cloud API keys required.

**12 phases | 35 lessons | 15 projects | ~28 hours | 100% local**

---

## What You Get

- **35 hands-on lessons** across 12 progressive phases -- from "What is a terminal?" to deploying full-stack AI apps
- **15 real-world projects** -- chatbots, RAG systems, AI agents, streaming apps, and more
- **AI-powered grading** -- every exercise is graded by real tests (60%) + AI rubric (40%)
- **Socratic AI tutor** -- a local LLM that guides you with questions, not answers
- **Zero cloud costs** -- everything runs locally via Ollama
- **Progress tracking** -- your progress is saved automatically, no account required. Create an account to sync across devices or for team/enterprise tracking

---

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

| Service | Port | URL |
|---------|------|-----|
| Next.js Web UI | 3000 | http://localhost:3000 |
| FastAPI Tutor Engine | 8000 | http://localhost:8000 |
| Ollama LLM Runtime | 11434 | http://localhost:11434 |
| Supabase Postgres | 54322 | -- |
| Supabase Auth | 9999 | -- |
| Supabase REST | 3001 | http://localhost:3001 |

---

## Quick Start

```bash
git clone https://github.com/user/learn-ai-with-grey8.git
cd learn-ai-with-grey8
bash scripts/setup.sh    # One-time setup: installs all dependencies, pulls AI model
bash scripts/start.sh    # Starts all services (Ollama, Tutor API, Web UI)
```

Open [http://localhost:3000](http://localhost:3000) to start learning.

For prerequisites (Python, Node.js, Ollama) and detailed instructions, see **[Getting Started](getting-started.md)**.

---

## Where to Go Next

| I want to... | Go to |
|--------------|-------|
| Set up my machine and start learning | [Getting Started](getting-started.md) |
| See all lessons, projects, and what I'll build | [Course Guide](course-guide.md) |
| Get certified after completing the bootcamp | [Certification](certification.md) |
| Hire AI developers or upskill my team | [For Employers](employers.md) |
| See all Grey8 services | [Services Overview](services.md) |
| Contribute content or code | [Contributing](contributing.md) |

---

## Browsing These Docs

You are viewing the documentation site. Here's how it works:

| Method | How | When |
|--------|-----|------|
| **GitHub Pages** (this site) | Automatic -- push to `main` and it updates | Online, shareable URL |
| **Locally** | `npx docsify-cli serve docs --port 4000` → http://localhost:4000 | Offline, during development |
| **GitHub repo** | Click any `.md` file in the `docs/` folder | Quick glance at raw content |

> **Maintainer note:** To enable GitHub Pages, go to **Settings > Pages** in your GitHub repo, set source to **Deploy from a branch**, branch to **`main`**, folder to **`/docs`**, and save. The site goes live in minutes.

---

## Monorepo Structure

```
curriculum/           Lesson content (Markdown, exercises, quizzes)
tutor/                FastAPI tutor engine (chat, grading, hints via Ollama)
platform/web/         Next.js 14 frontend (App Router, Tailwind)
platform/supabase/    Supabase migrations and config
ace/                  ACE framework CLI (generate, curate, sync, reflect)
docker/               Docker Compose files and Dockerfiles
docs/                 Documentation (you are here)
projects/             15 capstone project starters
scripts/              Setup and automation scripts
local-dev/            Local dev scripts (Ollama setup)
```
