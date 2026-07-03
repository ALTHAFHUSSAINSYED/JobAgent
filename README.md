# JobPilot AI
## Autonomous Multi-Agent Recruitment Platform

JobPilot AI is an enterprise-grade, event-driven, autonomous multi-agent recruitment platform designed to eliminate repetitive job searching and application tasks while maximizing interview conversion rates.

The platform is designed using **Clean Architecture** patterns, leveraging Python (FastAPI), React, PostgreSQL 17, Redis 7, and Playwright.

---

## Key Features (Phased Roadmap)
- **Modular Multi-Agent Core:** Independent specialized agents communicating asynchronously via a Redis event bus.
- **Adaptive Browser Agent:** Playwright controller utilizing accessibility semantics and DOM inspect heuristics instead of hardcoded layouts.
- **Resume Intelligence:** Automatically tailors LaTeX/PDF resumes to match targeted Job Descriptions.
- **Observability:** Custom correlation ID tracing across logging, database, queue layers, and Prometheus metrics tracking (`/metrics`).
- **Explainability Logging:** Records justifications for every match score, application skip, or manual intervention request.

---

## Technology Stack
- **Backend:** FastAPI, Async SQLAlchemy 2.0, Alembic, Pydantic v2
- **Frontend:** React, Vite, Vanilla CSS
- **Cache & Event Bus:** Redis 7
- **Database:** PostgreSQL 17
- **Telemetry:** Prometheus Metrics
- **Containerization:** Docker & Docker Compose

---

## Quickstart Setup

### 1. Clone & Configure local files
```bash
cp .env.example .env
cp config/profile.template.yaml config/profile.yaml
cp config/answers.template.yaml config/answers.yaml
```
*Configure your credentials, API keys (e.g. OpenRouter), and candidate details in the newly created local files.*

### 2. Manage the platform using Makefile
- **Start the platform:**
  ```bash
  make up
  ```
- **Inspect service logs:**
  ```bash
  make logs
  ```
- **Run tests:**
  ```bash
  make test
  ```
- **Apply migrations:**
  ```bash
  make migrate
  ```
- **Stop containers:**
  ```bash
  make down
  ```

---

## Architecture Layout
- **Presentation:** FastAPI API Routes and schemas.
- **Application:** Orchestrates Use Cases and business actions.
- **Domain:** Interface contracts and Candidate/Job domain entities.
- **Infrastructure:** Adapters including database repositories, Redis broker client, and Playwright verification hooks.
