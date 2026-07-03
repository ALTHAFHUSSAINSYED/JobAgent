# Sprint 1.5: Observability, Metrics & Testing Harness

This contract specifies the prometheus metrics instrumentation, diagnostics tests, and testing structures for JobPilot AI.

---

## 1. Goal
Implement runtime telemetry tracking via Prometheus middleware, expose a `/metrics` route on the FastAPI Gateway, configure async test harnesses with pytest, and verify 100% of application boundaries.

---

## 2. Directory Layout & Key Files
```text
backend/
├── app/
│   └── core/
│       └── metrics.py       # Prometheus middleware & metric indicators
└── tests/
    ├── conftest.py          # Pytest shared fixtures
    ├── application/
    │   └── test_use_cases.py# Use cases tests
    └── infrastructure/
        ├── test_database.py # Database connections and async repository tests
        └── test_event_bus.py# Event pub/sub tests
```

---

## 3. Specifications

### 3.1 Prometheus Observability Middleware
Configure custom middleware in FastAPI to capture operational metrics:

- **Metrics Tracked:**
  - `http_requests_total` (Counter): Total count of HTTP requests by method, path, and response status code.
  - `http_request_duration_seconds` (Histogram): Request latency buckets.
  - `db_connection_latency_seconds` (Gauge): Time taken to resolve `SELECT 1` queries on PostgreSQL.
  - `redis_connection_latency_seconds` (Gauge): Time taken to execute `PING` on Redis.
  - `system_uptime_seconds` (Counter/Gauge): System uptime tracking.
- **Route:** Expose standard `/metrics` endpoint read by Prometheus scrapers.

### 3.2 Testing Harness (pytest)
- **Async support:** Use `pytest-asyncio` library.
- **Configuration:** Write tests inside `tests/` matching the code hierarchy.
- **Fixtures (`conftest.py`):**
  - Setup async db engine connection for testing. Use local Postgres container or mock.
  - Setup clean Redis database block for isolated pub/sub test execution.

---

## 4. Acceptance Criteria
- Requesting `GET http://localhost:8000/metrics` returns standard Prometheus payload (plain text format).
- Prometheus payloads contain `db_connection_latency_seconds` and `redis_connection_latency_seconds` metrics.
- Running `pytest` runs and passes all 15+ target assertions on configurations, database operations, and pub/sub events.
