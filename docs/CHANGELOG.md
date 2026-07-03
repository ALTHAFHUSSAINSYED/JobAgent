# Changelog

All notable changes to the **JobPilot AI** project will be documented in this file.

---

## [Sprint 1.1] - 2026-07-03

### Files Created
- `docker-compose.yml` (Docker network/service orchestration)
- `backend/Dockerfile` (Backend python + Playwright runner)
- `backend/requirements.txt` (Python libraries list)
- `backend/app/main.py` (FastAPI lifecycles & router setup)
- `backend/app/core/config.py` (Pydantic Settings v2 loader)
- `backend/app/core/logging.py` (Structured logging engine)
- `backend/app/core/correlation.py` (X-Correlation-ID ContextVar)
- `backend/app/infrastructure/database.py` (Async engine & session helpers)
- `backend/app/presentation/routes.py` (FastAPI route registry for health checks)
- `backend/alembic.ini` (Alembic configuration metadata)
- `backend/alembic/env.py` (Database migration lifecycle integration)
- `backend/alembic/script.py.mako` (Migration script template)
- `backend/alembic/versions/.gitkeep` (Migration script placeholder)
- `frontend/Dockerfile` (Node.js production serve compile step)
- `frontend/vite.config.js` (Vite dev & server setup)
- `frontend/index.html` (Vite HTML template)
- `frontend/src/main.jsx` (React launcher index)
- `frontend/src/App.jsx` (React static main dashboard placeholder)
- `frontend/src/App.css` (React styling defaults)
- `docs/CHANGELOG.md` (Release/commit changelogs)

### Files Modified
- `docs/contracts/sprint_1_3_frontend.md` (Renamed from `docs/contracts/sprint_1_3_frontend_dashboard.md`)
- `docs/contracts/sprint_1_4_adapters.md` (Renamed from `docs/contracts/sprint_1_4_infrastructure_adapters.md`)
- `docs/contracts/sprint_1_5_testing.md` (Renamed from `docs/contracts/sprint_1_5_observability_and_tests.md`)

### Breaking Changes
None.

### Migrations Needed
None (migrations initialized but not populated yet).

### Rollback Steps
- To discard branch changes, switch to main: `git checkout main` and delete the branch: `git branch -D sprint-1.1`.
