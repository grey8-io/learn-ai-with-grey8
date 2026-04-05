"use client";

import { useState } from "react";

interface Project {
  id: number;
  name: string;
  slug: string;
  description: string;
  libraries: string[];
  model: string;
  phases: string;
  tier: "milestone" | "apply" | "systems" | "production";
}

const projects: Project[] = [
  { id: 1,  name: "AI Chatbot",               slug: "01-ai-chatbot",               description: "Multi-turn CLI chatbot with conversation history",                      libraries: ["requests", "rich"],                                          model: "llama3.2:3b", phases: "1-4",      tier: "milestone" },
  { id: 2,  name: "Document QA",              slug: "02-document-qa",              description: "Ingest PDFs into vectors, answer questions via RAG",                    libraries: ["requests", "chromadb", "PyPDF2"],                            model: "llama3.2:3b", phases: "6-7",      tier: "apply" },
  { id: 3,  name: "Code Review Agent",        slug: "03-code-review-agent",        description: "Parse Python files and get structured review feedback",                 libraries: ["requests", "pathlib"],                                       model: "llama3.2:3b", phases: "5, 8",     tier: "apply" },
  { id: 4,  name: "Semantic Search Engine",   slug: "04-semantic-search-engine",   description: "Embed documents and search by meaning via REST API",                    libraries: ["requests", "chromadb", "flask"],                             model: "llama3.2:3b", phases: "6",        tier: "systems" },
  { id: 5,  name: "RAG Knowledge Base",       slug: "05-rag-knowledge-base",       description: "Ingest Markdown notes, answer questions using RAG",                     libraries: ["requests", "chromadb", "pathlib"],                           model: "llama3.2:3b", phases: "6-7",      tier: "milestone" },
  { id: 6,  name: "Multi-Agent Pipeline",     slug: "06-multi-agent-pipeline",     description: "Chain Researcher/Writer/Reviewer agents for content",                   libraries: ["requests"],                                                  model: "llama3.2:3b", phases: "8",        tier: "systems" },
  { id: 7,  name: "AI-Powered API",           slug: "07-ai-powered-api",           description: "REST API with /summarize, /classify, /generate endpoints",              libraries: ["requests", "fastapi", "pydantic", "uvicorn"],                model: "llama3.2:3b", phases: "9",        tier: "milestone" },
  { id: 8,  name: "Streaming Chat App",       slug: "08-streaming-chat-app",       description: "SSE streaming from Ollama with HTML chat client",                       libraries: ["requests", "fastapi", "sse_starlette", "uvicorn"],           model: "llama3.2:3b", phases: "4, 9",     tier: "milestone" },
  { id: 9,  name: "AI Content Moderator",     slug: "09-ai-content-moderator",     description: "Classify text as safe/warning/unsafe using LLM",                       libraries: ["requests", "fastapi", "pydantic", "uvicorn"],                model: "llama3.2:3b", phases: "5, 9",     tier: "systems" },
  { id: 10, name: "Local Copilot",            slug: "10-local-copilot",            description: "Code completion endpoint via Flask + Ollama",                            libraries: ["requests", "flask"],                                         model: "llama3.2:3b", phases: "5, 8",     tier: "systems" },
  { id: 11, name: "AI Email Assistant",       slug: "11-ai-email-assistant",       description: "Generate professional emails from bullet points",                       libraries: ["requests", "rich"],                                          model: "llama3.2:3b", phases: "4-5",      tier: "apply" },
  { id: 12, name: "Image Description Service",slug: "12-image-description-service",description: "Multimodal LLM describes uploaded images",                              libraries: ["requests", "fastapi", "uvicorn"],                            model: "llava",       phases: "9",        tier: "production" },
  { id: 13, name: "AI Testing Framework",     slug: "13-ai-testing-framework",     description: "Generate pytest tests from Python source code",                         libraries: ["requests", "pathlib"],                                       model: "llama3.2:3b", phases: "5, 8",     tier: "production" },
  { id: 14, name: "Model Eval Dashboard",     slug: "14-model-evaluation-dashboard",description: "Compare models, track latency and quality metrics",                    libraries: ["requests", "pandas", "streamlit"],                           model: "llama3.2:3b", phases: "10",       tier: "production" },
  { id: 15, name: "Full-Stack AI SaaS",       slug: "15-full-stack-ai-saas",       description: "Complete app: FastAPI backend with RAG + HTML frontend",                libraries: ["requests", "fastapi", "chromadb", "Jinja2", "uvicorn"],      model: "llama3.2:3b", phases: "6-9, 11",  tier: "production" },
];

const tierConfig = {
  milestone: { label: "Milestone Project",     color: "bg-emerald-600/20 text-emerald-300", description: "Built during the course" },
  apply:     { label: "Apply What You Know",   color: "bg-primary-600/20 text-primary-300", description: "Phases 1-5 skills" },
  systems:   { label: "Build Real Systems",    color: "bg-amber-600/20 text-amber-300",     description: "Phases 6-9 skills" },
  production:{ label: "Production-Grade",      color: "bg-rose-600/20 text-rose-300",       description: "Phases 9-11 skills" },
};

type Filter = "all" | "milestone" | "apply" | "systems" | "production";

export default function ProjectsPage() {
  const [filter, setFilter] = useState<Filter>("all");

  const filtered = filter === "all" ? projects : projects.filter((p) => p.tier === filter);

  const filters: { key: Filter; label: string }[] = [
    { key: "all",        label: "All Projects" },
    { key: "milestone",  label: "Milestone" },
    { key: "apply",      label: "Apply" },
    { key: "systems",    label: "Systems" },
    { key: "production", label: "Production" },
  ];

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-slate-100">Capstone Projects</h1>
        <p className="mt-2 text-slate-400">
          15 real-world AI projects with starter code and reference solutions.
          Each project lives in{" "}
          <code className="rounded bg-slate-800 px-1.5 py-0.5 text-xs text-primary-300">
            projects/NN-name/
          </code>{" "}
          with TODO comments to guide you.
        </p>
      </div>

      {/* Filter tabs */}
      <div className="flex flex-wrap gap-2">
        {filters.map((f) => (
          <button
            key={f.key}
            onClick={() => setFilter(f.key)}
            className={`rounded-lg px-4 py-2 text-sm font-medium transition-all ${
              filter === f.key
                ? "bg-primary-600/20 text-primary-300 border border-primary-500/30"
                : "text-slate-400 hover:bg-slate-800 hover:text-slate-200 border border-transparent"
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Projects grid */}
      <div className="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
        {filtered.map((project) => {
          const tier = tierConfig[project.tier];
          return (
            <div
              key={project.id}
              className="card group relative transition-all hover:border-primary-500/50 hover:shadow-lg hover:shadow-primary-500/5"
            >
              {/* Project number badge */}
              <div className="absolute -top-3 -left-3 flex h-10 w-10 items-center justify-center rounded-full bg-primary-600 text-white text-sm font-bold shadow-lg shadow-primary-600/30">
                {String(project.id).padStart(2, "0")}
              </div>

              <div className="pt-2">
                <h3 className="text-lg font-semibold text-slate-100 group-hover:text-primary-300 transition-colors">
                  {project.name}
                </h3>
                <p className="mt-2 text-sm text-slate-400 leading-relaxed">
                  {project.description}
                </p>

                {/* Tier badge */}
                <div className="mt-3">
                  <span
                    className={`inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium ${tier.color}`}
                  >
                    {tier.label}
                  </span>
                </div>

                {/* Meta info */}
                <div className="mt-4 pt-3 border-t border-slate-700/50 space-y-2">
                  <div className="flex items-center gap-2 text-xs text-slate-500">
                    <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09Z" />
                    </svg>
                    <span>
                      Model:{" "}
                      <span className={project.model === "llava" ? "text-amber-400" : "text-slate-400"}>
                        {project.model}
                      </span>
                    </span>
                  </div>
                  <div className="flex items-center gap-2 text-xs text-slate-500">
                    <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" d="M4.26 10.147a60.438 60.438 0 0 0-.491 6.347A48.62 48.62 0 0 1 12 20.904a48.62 48.62 0 0 1 8.232-4.41 60.46 60.46 0 0 0-.491-6.347" />
                    </svg>
                    <span>Phases {project.phases}</span>
                  </div>
                </div>

                {/* Libraries */}
                <div className="mt-3 flex flex-wrap gap-1.5">
                  {project.libraries.map((lib) => (
                    <span
                      key={lib}
                      className="rounded bg-slate-800 px-1.5 py-0.5 text-[10px] text-slate-400 font-mono"
                    >
                      {lib}
                    </span>
                  ))}
                </div>

                {/* File path hint */}
                <div className="mt-3 text-[11px] text-slate-600 font-mono truncate">
                  projects/{project.slug}/starter/main.py
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Tip banner */}
      <div className="flex items-start gap-3 rounded-xl border border-primary-500/20 bg-primary-600/5 p-4">
        <svg
          className="h-5 w-5 shrink-0 text-primary-400 mt-0.5"
          fill="none"
          viewBox="0 0 24 24"
          strokeWidth={1.5}
          stroke="currentColor"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            d="M12 18v-5.25m0 0a6.01 6.01 0 0 0 1.5-.189m-1.5.189a6.01 6.01 0 0 1-1.5-.189m3.75 7.478a12.06 12.06 0 0 1-4.5 0m3.75 2.383a14.406 14.406 0 0 1-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 1 0-7.517 0c.85.493 1.509 1.333 1.509 2.316V18"
          />
        </svg>
        <div className="text-sm text-slate-300">
          <strong className="text-slate-200">Not sure which to pick?</strong>{" "}
          Start with <strong>Project 02 (Document QA)</strong> — it uses skills
          from every phase and makes an excellent portfolio piece. Each project
          has a <code className="rounded bg-slate-800 px-1 py-0.5 text-xs text-primary-300">reference/main.py</code> if
          you get stuck.
        </div>
      </div>
    </div>
  );
}
