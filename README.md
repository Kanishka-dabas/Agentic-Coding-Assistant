# 🤖 Agentic Coding Assistant

An autonomous coding agent that **plans, retrieves context, writes, scans, and executes Python code** — with human-in-the-loop approval, self-correction via a reflection/retry loop, and full observability. Built to demonstrate genuine multi-agent orchestration, not just a RAG chatbot.

**🔗 Live Demo:** [http://54.253.23.61:8501](http://54.253.23.61:8501)
**📦 Repository:** [github.com/Kanishka-dabas/Agentic-Coding-Assistant](https://github.com/Kanishka-dabas/Agentic-Coding-Assistant)

---

## What It Does

Given a plain-English coding task, the agent:

1. **Validates** the input for prompt-injection attempts
2. **Plans** a step-by-step approach using an LLM
3. **Retrieves** relevant context from its own codebase via RAG
4. **Writes** Python code to accomplish the task
5. **Scans** the generated code for dangerous patterns before it can run
6. **Pauses for human approval** before executing anything
7. **Executes** the approved code inside an isolated Docker sandbox
8. **Reflects and retries** (up to 3 times) if execution fails, before escalating to a human

Every step streams live to the UI, so the process is transparent — not a black box.

---

## Architecture

```
User Task
    │
    ▼
┌─────────────┐     blocked      ┌─────┐
│ Input Guard │ ───────────────► │ END │
└─────┬───────┘                  └─────┘
      │ safe
      ▼
┌─────────────┐
│   Planner   │  (LLM: breaks task into steps)
└─────┬───────┘
      ▼
┌─────────────┐
│  Retriever  │  (Qdrant: pulls relevant code from own codebase)
└─────┬───────┘
      ▼
┌─────────────┐  ◄────────────────────┐
│    Coder    │  (LLM: writes code)   │
└─────┬───────┘                       │
      ▼                               │
┌─────────────┐     blocked    ┌─────┐│
│ Code Guard  │ ─────────────► │ END ││
└─────┬───────┘                └─────┘│
      │ safe                          │
      ▼                               │
┌─────────────┐    rejected    ┌─────┐│
│    HITL     │ ─────────────► │ END ││
│  Approval   │                └─────┘│
└─────┬───────┘                       │
      │ approved                      │
      ▼                               │
┌─────────────┐   ✅ success   ┌─────┐│
│  Executor   │ ─────────────► │ END ││
│  (Docker)   │                └─────┘│
└─────┬───────┘                       │
      │ ❌ failure                    │
      ▼                               │
┌─────────────┐   max retries  ┌─────┐│
│  Reflector  │ ─────────────► │ END ││
└─────┬───────┘  reached       └─────┘│
      │ retry ────────────────────────┘
```

Orchestrated with **LangGraph** — conditional edges route around guardrail blocks and rejections, and a cyclical edge (`reflector → coder`) drives the self-correction loop.

---

## Key Features & Design Decisions

### 🛡️ Guardrails (defense in depth)
- **Input validation** — pattern-based prompt-injection detection on the raw task, before any LLM call
- **Code scanning** — static analysis blocks dangerous patterns (`os.system`, `eval`, `subprocess` with `shell=True`, network calls, file writes) *before* code ever reaches the sandbox
- **Retry limiter** — caps the reflection/retry loop at 3 attempts, then escalates instead of looping forever
- **Docker sandbox** — generated code runs in a throwaway container with `--network none`, memory/CPU caps, and a hard timeout

### 👤 Human-in-the-Loop
Uses LangGraph's `interrupt()` to pause the graph mid-execution and wait for explicit approval before running any generated code. Backed by a Postgres checkpointer, so the paused state survives a server restart.

### 🔍 RAG Over Its Own Codebase
The agent ingests its own source code into Qdrant (via `sentence-transformers` embeddings) so the coder node can retrieve and follow existing patterns instead of writing in a vacuum.

### 🔁 Reflection Loop
On execution failure, a dedicated reflector node analyzes the stack trace and produces a fix suggestion, which the coder node incorporates on the next attempt — a real self-correction cycle, not just a retry.

### 📊 Evaluation
Since LLM-generated code is non-deterministic, exact-match unit tests don't work well here. Instead, an **LLM-as-judge** framework (`backend/tests/eval/`) scores the agent's plan and generated code for correctness and relevance against a fixed set of representative tasks.

| Task | Score |
|---|---|
| Check if a number is prime | 5/5 |
| Reverse a string | 5/5 |
| Compute factorial | 5/5 |
| Find max value in a list | 5/5 |
| Count vowels in a string | 5/5 |

**Average judge score: 5.0/5**

Run it yourself:
```bash
cd backend
uv run python -m tests.eval.run_eval
```

### 📈 Observability
Every node execution, LLM call, and latency is traced via **LangSmith** — no black-box behavior, full visibility into what the agent did and why.

![LangSmith tracing dashboard showing node-level traces for the agent](assets/langsmith-tracing.png)

---

## Tech Stack

| Layer | Technology |
|---|---|
| Orchestration | LangGraph (StateGraph, conditional routing, `interrupt()`, checkpointing) |
| LLM | Groq (`openai/gpt-oss-120b`) |
| Backend | FastAPI, SSE streaming |
| Frontend | Streamlit |
| Sandbox | Docker (isolated, network-disabled, resource-capped execution) |
| Vector DB | Qdrant + `sentence-transformers` (`all-MiniLM-L6-v2`) |
| Memory | PostgreSQL (LangGraph checkpointing) |
| Observability | LangSmith |
| Deployment | AWS EC2, Docker Compose |
| CI/CD | GitHub Actions (lint + build) |
| Orchestration (design reference) | Kubernetes manifests for AKS-style deployment |

---

## Project Structure

```
agentic-coding-assistant/
├── backend/
│   ├── app/
│   │   ├── agent/          # LangGraph nodes, state, routing, prompts
│   │   ├── guardrails/     # input validation, code scanning, retry limiting
│   │   ├── sandbox/        # Docker-based isolated code execution
│   │   ├── rag/            # Qdrant ingestion + retrieval
│   │   ├── llm/            # LLM gateway/client
│   │   ├── memory/         # Postgres checkpointer
│   │   ├── api/            # FastAPI routes (chat, stream, HITL, sessions)
│   │   └── db/             # session history queries
│   └── tests/eval/         # LLM-as-judge evaluation framework
├── frontend/
│   └── streamlit_app/      # chat UI, live trace panel, HITL dialog
├── infra/
│   ├── k8s/                # Kubernetes manifests (design reference)
│   └── github-actions/     # CI pipeline
└── docker-compose.yml
```

---

## Running It Locally

**Prerequisites:** Docker, a Groq API key, `uv` (Python package manager)

```bash
git clone https://github.com/Kanishka-dabas/Agentic-Coding-Assistant.git
cd Agentic-Coding-Assistant
cp .env.example .env   # add your GROQ_API_KEY
docker compose up -d --build
```

Then open `http://localhost:8501`.

**Environment variables** (`.env`):
```
GROQ_API_KEY=your_key_here
GROQ_MODEL=openai/gpt-oss-120b
POSTGRES_URL=postgresql://postgres:postgres@postgres:5432/agentic
QDRANT_HOST=qdrant

# Optional — enables tracing
LANGSMITH_TRACING=true
LANGSMITH_API_KEY=your_key_here
LANGSMITH_PROJECT=agentic-coding-assistant
```

---

## Deployment Notes

Deployed on a single AWS EC2 instance (`t3.small`) running the full stack via Docker Compose (backend, frontend, Postgres, Qdrant), with an Elastic IP for a stable address and `restart: unless-stopped` policies so services recover automatically after a reboot.

Kubernetes manifests (`infra/k8s/`) are included as a design reference for an AKS-style deployment with autoscaling and health checks — the live demo runs on the simpler EC2 setup for cost efficiency at portfolio scale.

**Note on sandboxing:** the code executor spins up a fresh, network-isolated Docker container per execution. Since the backend itself runs inside a container in production, it talks to the *host's* Docker daemon via a mounted socket — a common Docker-in-Docker pattern, with paths resolved from the host's perspective to keep the mount valid.

---

## CI/CD

GitHub Actions runs on every push to `main`: lint (`ruff`) → Docker build verification for both backend and frontend images.

---

## What I'd Add Next

- Per-user session isolation (currently session history is scoped to the browser tab to avoid leaking one visitor's conversations to another on the shared demo link)
- LLM provider fallback in the gateway layer for rate-limit resilience
- Extending the eval suite to run in CI with secrets management