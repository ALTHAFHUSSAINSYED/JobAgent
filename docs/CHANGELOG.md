# Changelog

All notable changes to the **JobPilot AI** project will be documented in this file.

---

## [Sprint 1.5] - 2026-07-03

### Files Created
- `backend/app/core/metrics.py` (Prometheus HTTP requests metrics Counter and Histogram trackers)
- `pyproject.toml` (Ruff linter standards and pytest cov configurations)
- `mypy.ini` (MyPy static type checker configuration setup)
- `.pre-commit-config.yaml` (Pre-commit hooks checking format rules)
- `.github/workflows/ci.yml` (Continuous integration workflow executing checks and pytest suite)

### Files Modified
- `backend/requirements.txt` (Appended `pytest-cov` dependency)
- `backend/app/main.py` (Registered PrometheusMiddleware and exposed `/metrics` endpoints)
- `docker-compose.yml` (Added backend healthchecks and mapped depends_on condition: service_healthy criteria)

---

## [Sprint 1.4] - 2026-07-03

### Files Created
- `backend/app/infrastructure/repositories/resume.py` (Resumes scanning logic, file sizes, last modified times, and SHA-256 hashes computations)
- `backend/app/infrastructure/config/watcher.py` (Hot-reloading config watchers file modification time checker)

### Files Modified
- `backend/app/main.py` (FastAPI startup validation checker, and Redis EventBus listener subscriptions lifecycle setup)
- `backend/app/presentation/routes.py` (Exposed GET `/dashboard`, GET `/system/info`, GET `/configuration`, GET `/logs`, GET `/version`, and multi-channel WebSockets `/ws/logs`, `/ws/system`, `/ws/events`)
- `backend/app/application/dto.py` (Extended `DashboardDTO` mapping dynamic latency stats, database connection pool statistics, and scanned resumes list)
- `backend/app/application/handlers.py` (Integrated database, Redis event bus, and OpenRouter HEAD latency checks; mapped database connection pools size metrics; scanned resumes metadata, size, timestamps, and hashes)
- `backend/app/infrastructure/providers/dependencies.py` (Injected resume manager repository)
- `backend/app/infrastructure/config/yaml_loader.py` (Configuration schemas check_placeholders brackets validator and experience strings format parser)
- `backend/app/infrastructure/browser_client.py` (Playwright verifier detail scanner extracting Chromium installation versions and executable paths)
- `backend/app/infrastructure/llm_client.py` (Async OpenRouter connectivity checks measuring request latencies)
- `frontend/src/App.jsx` (Responsive modern self-diagnosing dashboard showcasing DB connection pool details, PostgreSQL, Redis, and OpenRouter latency measurements, scanned resumes table registry, and multi-channel sockets connection stats)
- `docs/CHANGELOG.md` (Release/commit changelogs)

### Breaking Changes
- Dashboard schema (`DashboardDTO`) now requires `latencies`, `database_pool`, `resumes`, and `playwright_details` keys.

### Migrations Needed
None.

### Rollback Steps
- To discard branch changes, switch to main: `git checkout main` and delete the branch: `git branch -D sprint-1.4`.

---

## [Sprint 1.3] - 2026-07-03

### Files Created
- `frontend/tailwind.config.js` (Tailwind CSS compile configuration settings)
- `frontend/postcss.config.js` (PostCSS compiler integration)
- `backend/app/application/__init__.py` (Application package setup)
- `backend/app/domain/__init__.py` (Domain package setup)
- `backend/app/infrastructure/__init__.py` (Infrastructure package setup)

### Files Modified
- `backend/app/core/logging.py` (Structured JSON logging format & in-memory logging histories queue)
- `backend/app/application/dto.py` (SystemInfo, Configuration snapshot, Version, and Dashboard overview payload models)
- `backend/app/application/queries.py` (Dashboard queries mapping schema definitions)
- `backend/app/application/handlers.py` (SystemInfo, Configuration snapshot, Version, and Dashboard queries handlers)
- `backend/app/infrastructure/providers/dependencies.py` (Dependency injection setup mapping new dashboard queries)
- `backend/app/presentation/routes.py` (Exposed GET /dashboard, GET /system/info, GET /configuration, GET /logs, GET /version, and WebSocket logs stream route)
- `frontend/package.json` (Vite packages update with tailwindcss, postcss, autoprefixer, and lucide-react dependencies)
- `frontend/src/App.css` (Tailwind CSS directives setup)
- `frontend/src/App.jsx` (Responsive modern dark theme dashboard matching shadcn UI aesthetics, with streaming websockets logs terminal viewer)

### Breaking Changes
None.

### Migrations Needed
None.

### Rollback Steps
- To discard branch changes, switch to main: `git checkout main` and delete the branch: `git branch -D sprint-1.3`.
