#!/bin/bash
# Create full project directory structure

# GitHub
mkdir -p .github/workflows .github/ISSUE_TEMPLATE

# Curriculum - 12 phases
for phase in \
  "phase-01-dev-environment/lesson-01-terminal-and-git" \
  "phase-01-dev-environment/lesson-02-python-setup" \
  "phase-01-dev-environment/lesson-03-vscode-setup" \
  "phase-02-python-foundations/lesson-01-variables-and-functions" \
  "phase-02-python-foundations/lesson-02-data-structures" \
  "phase-02-python-foundations/lesson-03-apis-and-json" \
  "phase-03-ai-fundamentals/lesson-01-what-is-ai" \
  "phase-03-ai-fundamentals/lesson-02-llms-and-tokens" \
  "phase-03-ai-fundamentals/lesson-03-ai-limitations" \
  "phase-04-first-ai-app/lesson-01-calling-llm-apis" \
  "phase-04-first-ai-app/lesson-02-building-cli-assistant" \
  "phase-05-prompt-engineering/lesson-01-role-prompting" \
  "phase-05-prompt-engineering/lesson-02-structured-outputs" \
  "phase-05-prompt-engineering/lesson-03-few-shot-patterns" \
  "phase-06-embeddings-and-search/lesson-01-what-are-embeddings" \
  "phase-06-embeddings-and-search/lesson-02-vector-databases" \
  "phase-06-embeddings-and-search/lesson-03-semantic-search" \
  "phase-07-rag-systems/lesson-01-rag-architecture" \
  "phase-07-rag-systems/lesson-02-document-chunking" \
  "phase-07-rag-systems/lesson-03-building-rag-pipeline" \
  "phase-08-ai-agents/lesson-01-agent-concepts" \
  "phase-08-ai-agents/lesson-02-tool-use" \
  "phase-08-ai-agents/lesson-03-multi-agent-systems" \
  "phase-09-ai-backend/lesson-01-fastapi-basics" \
  "phase-09-ai-backend/lesson-02-async-ai-services" \
  "phase-09-ai-backend/lesson-03-production-patterns" \
  "phase-10-optimization/lesson-01-token-cost-control" \
  "phase-10-optimization/lesson-02-caching-and-batching" \
  "phase-10-optimization/lesson-03-latency-optimization" \
  "phase-11-deployment/lesson-01-docker-basics" \
  "phase-11-deployment/lesson-02-cloud-deployment" \
  "phase-11-deployment/lesson-03-monitoring"
do
  mkdir -p "curriculum/$phase/exercises/ex-01/starter"
  mkdir -p "curriculum/$phase/exercises/ex-01/solution"
  mkdir -p "curriculum/$phase/exercises/ex-01/tests"
  mkdir -p "curriculum/$phase/diagrams"
done

mkdir -p curriculum/phase-12-capstone

# Platform
mkdir -p platform/web/app/auth/login
mkdir -p platform/web/app/auth/register
mkdir -p platform/web/app/learn/phases
mkdir -p platform/web/app/learn/lessons
mkdir -p platform/web/app/learn/exercises
mkdir -p platform/web/app/tutor/chat
mkdir -p platform/web/app/api/tutor
mkdir -p platform/web/app/api/grade
mkdir -p platform/web/app/api/content
mkdir -p platform/web/components
mkdir -p platform/web/lib
mkdir -p platform/web/public
mkdir -p platform/supabase/migrations

# Tutor engine
mkdir -p tutor/tutor/routers
mkdir -p tutor/tutor/engine
mkdir -p tutor/tutor/grading
mkdir -p tutor/tutor/models
mkdir -p tutor/tests

# ACE framework
mkdir -p ace/ace/generator/templates
mkdir -p ace/ace/curator
mkdir -p ace/ace/reflector
mkdir -p ace/ace/shared
mkdir -p ace/tests

# Local dev
mkdir -p local-dev/scripts
mkdir -p local-dev/configs
mkdir -p local-dev/agents

# Projects
for i in 01-ai-chatbot 02-document-qa 03-code-review-agent 04-semantic-search-engine \
  05-rag-knowledge-base 06-multi-agent-pipeline 07-ai-powered-api 08-streaming-chat-app \
  09-ai-content-moderator 10-local-copilot 11-ai-email-assistant 12-image-description-service \
  13-ai-testing-framework 14-model-evaluation-dashboard 15-full-stack-ai-saas
do
  mkdir -p "projects/$i/starter"
  mkdir -p "projects/$i/reference"
done

# Docker & docs
mkdir -p docker
mkdir -p docs/adr
mkdir -p docs/guides

echo "Directory structure created successfully!"
