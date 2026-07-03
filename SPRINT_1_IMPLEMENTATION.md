# Sprint 1 Master Implementation Contract
## JobPilot AI — Autonomous Multi-Agent Recruitment Platform

This document serves as the master contract for the implementation of **Sprint 1**. To ensure high-quality, robust delivery, the implementation of this sprint is divided into **five sub-contracts** representing modular slices of the system.

---

## 1. Core Architectural Pillars (Updated)

To support enterprise-grade extensibility, testing, and observability, the following architectural rules are locked in:

1. **Clean Architecture:** The application logic is strictly separated into:
   - **Presentation Layer:** REST API schemas and FastAPI route controllers.
   - **Application Layer:** Use Cases (Interactors) orchestrating business logic and DTOs.
   - **Domain Layer:** Pure python Entities and Abstract Interfaces (no framework dependencies).
   - **Infrastructure Layer:** Database adapters, Redis event bus, client verifications, and external APIs.
2. **Asynchronous DB (SQLAlchemy Async + asyncpg):** No synchronous engine blocks are allowed. The database uses asynchronous sessions and the `asyncpg` driver for non-blocking I/O.
3. **Decoupled Interfaces:** The business layer interacts strictly with `IEventBus` and `IRepository`. No direct references to Redis client objects or database engines are allowed outside of the Infrastructure layer.
4. **Observability Middleware:** The server includes custom middleware to inject `X-Correlation-ID` tracking headers and tracks telemetry metrics (request latency, database ping latency, redis ping latency) exposed at a `/metrics` route.
5. **pgAdmin integration:** A pgAdmin 4 UI container is included in the Docker network to simplify database schema inspection.

---

## 2. Sprint 1 Sub-Contracts

Sprint 1 is divided into five incremental sub-contracts. Refer to each document for detailed file schemas, dependencies, and code layouts:

1. **[Sprint 1.1: Infrastructure & Docker Compose Setup](file:///d:/JobAgent/docs/contracts/sprint_1_1_infrastructure.md)**
   - Setup: Postgres 17, Redis 7, pgAdmin, and network volume configurations.
2. **[Sprint 1.2: Backend Core & Async Database Integration](file:///d:/JobAgent/docs/contracts/sprint_1_2_backend_core.md)**
   - Setup: FastAPI bootstrap, Correlation ID middleware, logging formatting, Async SQLAlchemy engine, and Alembic migrations.
3. **[Sprint 1.3: Frontend Dashboard Integration](file:///d:/JobAgent/docs/contracts/sprint_1_3_frontend_dashboard.md)**
   - Setup: React (Vite), vanilla CSS dark premium design dashboard, diagnostics logs monitor, and periodic status polling.
4. **[Sprint 1.4: Infrastructure Adapters & API Gateways](file:///d:/JobAgent/docs/contracts/sprint_1_4_infrastructure_adapters.md)**
   - Setup: Abstract `IEventBus`, `RedisEventBus` adapter, generic repository, verifiers for Playwright/OpenRouter, and yaml validators.
5. **[Sprint 1.5: Observability, Metrics & Testing Harness](file:///d:/JobAgent/docs/contracts/sprint_1_5_observability_and_tests.md)**
   - Setup: Prometheus middleware telemetry, `/metrics` endpoint, pytest async configuration fixtures, and test coverage metrics.

---

## 3. Core Directory Layout

```text
backend/
├── app/
│   ├── main.py                  # FastAPI initialization & lifecycles
│   │
│   ├── core/                    # System-wide configuration files
│   │   ├── config.py            # Pydantic Settings v2
│   │   ├── logging.py           # Logging format config
│   │   ├── correlation.py       # Correlation ID tracking middleware
│   │   └── metrics.py           # Prometheus instrumentation middleware
│   │
│   ├── domain/                  # Pure Business Logic (No frameworks/DBs)
│   │   ├── entities.py          # Data classes (Candidate, Job, Application)
│   │   └── interfaces.py        # Abstract ABC interfaces (Repositories, EventBus)
│   │
│   ├── application/             # Use cases, orchestrators, and services
│   │   ├── use_cases.py         # Config validation and health check logic
│   │   └── dtos.py              # Data Transfer Objects
│   │
│   ├── infrastructure/          # Frameworks, database, libraries, and APIs
│   │   ├── database.py          # Async engine, sessionmaker, and Base models
│   │   ├── repositories.py      # Async generic DB base & concrete repositories
│   │   ├── event_bus.py         # Redis Pub/Sub EventBus implementation
│   │   ├── config_parser.py     # YAML Pydantic schema validation
│   │   └── browser_client.py    # Playwright verification client
│   │
│   └── presentation/            # Controllers and HTTP endpoints
│       ├── routes.py            # APIRouter paths (/health, /dashboard)
│       └── schemas.py           # Request/response JSON schemas
│
├── alembic.ini                  # Alembic configurations
├── Dockerfile                   # Backend Docker configuration
├── requirements.txt             # Python packages
└── tests/                       # Pytest test suites matching app structure
```

---

## 4. Acceptance Criteria

Sprint 1 is considered complete if and only if:
- `docker compose up -d` successfully builds and launches all 5 services.
- Database and Cache status indicators on the React UI dashboard turn green (Connected).
- Every server HTTP response contains the `X-Correlation-ID` header.
- `/metrics` returns standard Prometheus payload metrics including DB/Redis latencies.
- All unit and integration tests run and pass via `pytest` with 100% success rate.
