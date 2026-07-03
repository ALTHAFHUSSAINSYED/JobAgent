# Sprint 1 Implementation Contract
## JobPilot AI — Autonomous Multi-Agent Recruitment Platform

This document serves as a strict, non-negotiable contract for the implementation of **Sprint 1**. Every module, class, database schema, API path, and configuration schema defined here must be implemented precisely as described.

---

## 1. Sprint Goal

Establish the architectural and deployment foundation of JobPilot AI using **Clean Architecture** principles. By the end of this sprint, the platform must successfully run a containerized stack (FastAPI, React, PostgreSQL 17, and Redis 7) via Docker Compose, perform configuration and credential validations, connect to database and cache backends, verify system dependencies (Playwright and OpenRouter), and serve a unified, live **Health Dashboard** indicating that the system is ready for subsequent automation loops.

---

## 2. Scope

### In-Scope
- **Infrastructure Services:** PostgreSQL 17, Redis 7, and Playwright binary environment.
- **Backend Framework:** FastAPI with SQLAlchemy 2.0 and Alembic migrations.
- **Frontend Framework:** Simple, premium-designed single-page React app (Vite-based) for the dashboard.
- **Settings & Config:** Dynamic environment variable loading (`.env` via Pydantic Settings v2) and YAML configuration parsing/validations (`profile.yaml`, `answers.yaml`, `companies.yaml`).
- **Domain Modeling:** Decoupled Entities and Abstract Repository/Broker interfaces.
- **API Interfaces:** REST endpoints for system health and configuration status.
- **Testing:** Unit tests verifying configuration loading, DB connectivity, and Redis event loop connectivity.
- **Docker Compose Orchestration:** Seamless build and runtime setup (`docker compose up -d`).

### Out-of-Scope (Deferred to Sprints 2-5)
- Active web scraping and parsing of real Job Descriptions.
- Automated application filling or browser actions via Playwright.
- Active AI-based resume tailoring or LLM text generation.
- Full event handler workers (only core event publishing/subscribing interfaces are configured).

---

## 3. Directory Layout Specification

The backend code must adhere to the following Clean Architecture directory structure:

```text
backend/
├── app/
│   ├── main.py                  # FastAPI app registry and startup hooks
│   │
│   ├── core/                    # System-wide configuration files
│   │   ├── __init__.py
│   │   ├── config.py            # Pydantic BaseSettings loading .env
│   │   ├── logging.py           # DictConfig logging configuration
│   │   └── events.py            # Core event schemas and types
│   │
│   ├── domain/                  # Pure Business Logic (No frameworks, DBs, or libs)
│   │   ├── __init__.py
│   │   ├── entities.py          # Data classes (Candidate, Job, Application)
│   │   └── interfaces.py        # Abstract Base Classes (Repositories, EventBus)
│   │
│   ├── application/             # Use cases, orchestrators, and services
│   │   ├── __init__.py
│   │   ├── use_cases.py         # Config validation and health checker services
│   │   └── dtos.py              # Data Transfer Objects for boundaries
│   │
│   ├── infrastructure/          # Frameworks, database, libraries, and APIs
│   │   ├── __init__.py
│   │   ├── database.py          # SQLAlchemy engine, session maker, base model
│   │   ├── repositories.py      # SQLAlchemy repository implementations
│   │   ├── event_bus.py         # Redis event publisher/subscriber implementations
│   │   ├── config_parser.py     # YAML loader and Pydantic validators
│   │   └── browser_client.py    # Playwright verification module
│   │
│   └── presentation/            # Controllers and HTTP endpoints
│       ├── __init__.py
│       ├── routes.py            # FastAPI APIRouter endpoints
│       └── schemas.py           # API request/response JSON validators
│
├── alembic.ini                  # Alembic migration configuration
├── Dockerfile                   # Backend Docker build instructions
├── requirements.txt             # Python packages list
└── tests/                       # Pytest test suites matching app structure
```

---

## 4. File Specifications

### 4.1 Entrypoints & Core Configurations

#### File: `backend/app/main.py`
- **Purpose:** Serve as the FastAPI application initializer.
- **Responsibilities:**
  - Instantiate `FastAPI` application with title `JobPilot AI API`.
  - Wire middleware (CORS middleware allowing frontend origins).
  - Register routers from `presentation/routes.py`.
  - Configure startup/shutdown lifetime hooks to verify DB connection, initialize Redis event listener, and register core services.
- **Dependencies:** `fastapi`, `core.config`, `presentation.routes`, `infrastructure.database`.

#### File: `backend/app/core/config.py`
- **Purpose:** Declare the system settings object.
- **Responsibilities:**
  - Define `Settings` class inheriting from `pydantic_settings.BaseSettings`.
  - Validate environment variables: `DATABASE_URL`, `REDIS_URL`, `OPENROUTER_API_KEY`, `PORT`, `ENV`.
  - Expose default fallback settings for local developments.
- **Dependencies:** `pydantic-settings`.

#### File: `backend/app/core/logging.py`
- **Purpose:** Setup unified logger formatting.
- **Responsibilities:**
  - Define a logging configuration dictionary (`LOGGING_CONFIG`).
  - Standardize log output format: `[%(asctime)s] [%(levelname)s] [%(name)s:%(lineno)d] - %(message)s`.
  - Direct logs to both standard output (`StreamHandler`) and a rotating file handler inside `logs/app.log`.

---

### 4.2 Domain Layer

#### File: `backend/app/domain/entities.py`
- **Purpose:** Define pure python domain objects representing entities.
- **Responsibilities:**
  - Define `Candidate` dataclass.
  - Define `Job` dataclass.
  - Define `Application` dataclass.
  - No database annotations or external framework code is permitted inside this file.
- **Dependencies:** None.

#### File: `backend/app/domain/interfaces.py`
- **Purpose:** Expose abstract interfaces for data repositories and integration adapters.
- **Responsibilities:**
  - Define `ICandidateRepository(ABC)` with abstract methods `get_by_email()`, `save()`.
  - Define `IJobRepository(ABC)` with abstract methods `get_by_id()`, `save()`, `list()`.
  - Define `IApplicationRepository(ABC)` with abstract methods `save()`, `get_by_id()`, `list()`.
  - Define `IEventBus(ABC)` with abstract methods `publish(event_name, payload)`, `subscribe(event_name, handler)`.
- **Dependencies:** `abc`, `domain.entities`.

---

### 4.3 Application Layer

#### File: `backend/app/application/use_cases.py`
- **Purpose:** Handle user actions and orchestration workflows.
- **Responsibilities:**
  - Implement `ValidateConfigurationUseCase` that:
    1. Triggers the configuration parser infrastructure.
    2. Validates `profile.yaml`, `answers.yaml`, and `companies.yaml` schemas.
    3. Returns validation success flags and descriptive error logs on failures.
  - Implement `CheckSystemHealthUseCase` that:
    1. Pings the DB infrastructure using standard SQL query (`SELECT 1`).
    2. Pings Redis cache (`PING` command).
    3. Checks Playwright browser installation status.
    4. Evaluates if the OpenRouter API key environment variable is configured.
    5. Aggregates the results into a unified health state object.
- **Dependencies:** `domain.interfaces`, `application.dtos`.

---

### 4.4 Infrastructure Layer

#### File: `backend/app/infrastructure/database.py`
- **Purpose:** Configure database connection hooks.
- **Responsibilities:**
  - Create SQLAlchemy engine using `create_engine()` configured for PostgreSQL.
  - Setup `sessionmaker` bound to the engine.
  - Define `Base` declarative model base class using `declarative_base()`.
  - Expose a thread-safe session generator (`get_db_session()`).
- **Dependencies:** `sqlalchemy`.

#### File: `backend/app/infrastructure/repositories.py`
- **Purpose:** Concrete implementations of repositories using SQLAlchemy.
- **Responsibilities:**
  - Implement `SQLAlchemyCandidateRepository` executing database sessions to query/persist candidates.
  - Implement `SQLAlchemyJobRepository` and `SQLAlchemyApplicationRepository`.
  - Map SQLAlchemy model tables to Domain Entities.
- **Dependencies:** `domain.interfaces`, `infrastructure.database`, `sqlalchemy`.

#### File: `backend/app/infrastructure/event_bus.py`
- **Purpose:** Establish real-time communication pipeline using Redis.
- **Responsibilities:**
  - Implement `RedisEventBus` utilizing Redis Pub/Sub commands.
  - Support non-blocking listener threads processing messages from channel subscriptions.
- **Dependencies:** `domain.interfaces`, `redis`.

#### File: `backend/app/infrastructure/config_parser.py`
- **Purpose:** Load and validate configuration profiles.
- **Responsibilities:**
  - Define Pydantic validation schemas matching profile parameters:
    - `ProfileConfigSchema` (maps `profile.yaml`).
    - `AnswersConfigSchema` (maps `answers.yaml`).
    - `CompaniesConfigSchema` (maps `companies.yaml`).
  - Read YAML files and instantiate schemas, raising validation exceptions for misformatted data.
- **Dependencies:** `pydantic`, `pyyaml`.

#### File: `backend/app/infrastructure/browser_client.py`
- **Purpose:** Verify the presence of headless browser runtimes.
- **Responsibilities:**
  - Implement `PlaywrightVerifier` checking if Playwright library imports successfully and can resolve execution paths for Chromium.
- **Dependencies:** `playwright`.

---

### 4.5 Presentation Layer

#### File: `backend/app/presentation/routes.py`
- **Purpose:** Map API routes to endpoints.
- **Responsibilities:**
  - Define `/api/v1/health` (GET) returning raw system backend checks.
  - Define `/api/v1/dashboard` (GET) resolving full environment status (DB, Redis, Playwright, configuration status, resume stats).
  - Inject dependencies using standard FastAPI `Depends` wrapper patterns.
- **Dependencies:** `fastapi`, `application.use_cases`.

---

## 5. Docker Orchestration

The platform runs inside a multi-container network. The following `docker-compose.yml` configures this topology:

```yaml
version: '3.8'

services:
  postgres:
    image: postgres:17-alpine
    container_name: jobpilot_postgres
    restart: always
    environment:
      POSTGRES_DB: jobpilot_db
      POSTGRES_USER: jobpilot_user
      POSTGRES_PASSWORD: jobpilot_secure_password
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U jobpilot_user -d jobpilot_db"]
      interval: 5s
      timeout: 5s
      retries: 5

  redis:
    image: redis:7-alpine
    container_name: jobpilot_redis
    restart: always
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 5s
      retries: 5

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    container_name: jobpilot_backend
    restart: always
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://jobpilot_user:jobpilot_secure_password@postgres:5432/jobpilot_db
      - REDIS_URL=redis://redis:6379/0
      - OPENROUTER_API_KEY=${OPENROUTER_API_KEY}
      - ENV=production
    volumes:
      - ./config:/app/config
      - ./resumes:/app/resumes
      - ./logs:/app/logs
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    container_name: jobpilot_frontend
    restart: always
    ports:
      - "3000:3000"
    depends_on:
      - backend

volumes:
  postgres_data:
  redis_data:
```

---

## 6. Database Models & Schema Specifications

The backend infrastructure layer exposes the following database models extending SQLAlchemy `Base`:

### Model: `CandidateModel`
- **Table Name:** `candidates`
- **Columns:**
  - `id`: `UUID`, Primary Key, Defaults to `uuid.uuid4`.
  - `full_name`: `String(255)`, Non-Nullable.
  - `email`: `String(255)`, Non-Nullable, Unique index.
  - `phone`: `String(50)`, Nullable.
  - `profile_url`: `String(500)`, Nullable.
  - `created_at`: `DateTime`, Non-Nullable, Defaults to current timestamp.

### Model: `JobModel`
- **Table Name:** `jobs`
- **Columns:**
  - `id`: `UUID`, Primary Key, Defaults to `uuid.uuid4`.
  - `portal_id`: `String(100)`, Nullable.
  - `portal_name`: `String(100)`, Nullable.
  - `company_name`: `String(255)`, Non-Nullable.
  - `job_title`: `String(255)`, Non-Nullable.
  - `job_description`: `Text`, Non-Nullable.
  - `salary_range`: `String(100)`, Nullable.
  - `match_score`: `Numeric(5,2)`, Nullable.
  - `status`: `String(50)`, Default: `'unprocessed'`.
  - `created_at`: `DateTime`, Defaults to current timestamp.

### Model: `ApplicationModel`
- **Table Name:** `applications`
- **Columns:**
  - `id`: `UUID`, Primary Key, Defaults to `uuid.uuid4`.
  - `candidate_id`: `UUID`, ForeignKey referencing `candidates.id`.
  - `job_id`: `UUID`, ForeignKey referencing `jobs.id`.
  - `status`: `String(50)`, Non-Nullable.
  - `tailored_resume_path`: `String(500)`, Nullable.
  - `submitted_payload`: `Text`, Nullable.
  - `submitted_at`: `DateTime`, Defaults to current timestamp.

---

## 7. API Endpoints

### 7.1 System Health endpoint
- **Path:** `/api/v1/health`
- **Method:** `GET`
- **Description:** Basic service availability heartbeat check.
- **Success Response (200 OK):**
  ```json
  {
    "status": "healthy",
    "timestamp": "2026-07-03T15:40:00Z"
  }
  ```

### 7.2 Health Dashboard Endpoint
- **Path:** `/api/v1/dashboard`
- **Method:** `GET`
- **Description:** Complete architectural interface diagnostic status resolver.
- **Success Response (200 OK):**
  ```json
  {
    "backend": "online",
    "connections": {
      "database": "connected",
      "redis": "connected",
      "playwright": "installed",
      "openrouter": "ready"
    },
    "configuration": {
      "valid": true,
      "profile_loaded": true,
      "resume_found": true,
      "resumes_count": 2
    },
    "system_timestamp": "2026-07-03T15:40:00Z"
  }
  ```

---

## 8. Frontend Structure & Design

The frontend module represents a single-page React client styled with vanilla CSS following a dark, premium aesthetic:

- **Directory:** `/frontend`
- **Build Engine:** Vite
- **UI Sections:**
  - **Header:** Premium title displaying `JobPilot AI Orchestration Engine` with system runtime counters.
  - **Service Status Grid:** Four high-fidelity indicator cards displaying status (Green/Red) for API, Database, Event Bus, and Browser Engine.
  - **Profile Information Panel:** Displays candidate name, parsed contact info, and loaded configurations.
  - **Diagnostics Console:** Real-time log monitor detailing system initialization events.

---

## 9. Testing Specifications

A suite of unit and integration tests must be executed with Pytest to guarantee that the system starts correctly.

### Test Coverage Checklist
1. **Config Parser Tests (`tests/infrastructure/test_config_parser.py`):**
   - Verify that configurations raise `ValidationError` when required parameters are omitted.
   - Verify successfully parsed objects contain valid nested objects.
2. **Database Connection Tests (`tests/infrastructure/test_database.py`):**
   - Verify that the active database session can run a `SELECT 1` query.
   - Verify candidate profile insertion and retrieval cycles.
3. **Event Bus Connection Tests (`tests/infrastructure/test_event_bus.py`):**
   - Verify connection to the local Redis engine.
   - Verify a mock event publisher can broadcast to a channel and be read by a subscriber thread.
4. **Use Case Tests (`tests/application/test_use_cases.py`):**
   - Verify `CheckSystemHealthUseCase` reports correctly when services are active versus offline.

---

## 10. Acceptance Criteria

Sprint 1 is considered successful if and only if **all** of the following validation checks pass without errors:

1. **Docker Compose Build:** `docker compose build` succeeds with zero warning exit codes.
2. **Docker Compose Up:** `docker compose up -d` starts `backend`, `frontend`, `postgres`, and `redis` containers successfully.
3. **Database Health:** PostgreSQL container returns healthy and registers schemas.
4. **Redis Health:** Redis container processes requests and responds to `PING` with `PONG`.
5. **Backend Health API:** Requesting `GET http://localhost:8000/api/v1/health` returns `200 OK`.
6. **Backend Dashboard API:** Requesting `GET http://localhost:8000/api/v1/dashboard` returns `200 OK` indicating `database: connected`, `redis: connected`, `playwright: installed`, and `openrouter: ready`.
7. **Migrations Active:** Running `alembic upgrade head` succeeds against the running PostgreSQL container.
8. **Logging Active:** Server startup writes structured info statements to `logs/app.log`.
9. **React UI Active:** Accessing `http://localhost:3000` loads the premium status page.
10. **Test Coverage:** Running `pytest` in the backend workspace root executes all validation suites successfully with 100% pass rate.
