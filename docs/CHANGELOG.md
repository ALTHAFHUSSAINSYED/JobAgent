# Changelog

All notable changes to the **JobPilot AI** project will be documented in this file.

---

## [Sprint 1.2] - 2026-07-03

### Files Created
- `backend/alembic/versions/001_initial_schema.py` (Initial database tables migration schema)
- `backend/app/domain/exceptions.py` (Custom domain error rules)
- `backend/app/domain/value_objects.py` (Domain status enums)
- `backend/app/domain/entities.py` (Pure candidate, job, and application definitions)
- `backend/app/domain/interfaces.py` (Abstract base repository, UnitOfWork, and EventBus interfaces)
- `backend/app/application/dto.py` (Pydantic Health and Configuration status DTOs)
- `backend/app/application/commands.py` (ValidateConfigurationCommand)
- `backend/app/application/queries.py` (HealthCheckQuery)
- `backend/app/application/handlers.py` (ValidateConfigurationUseCase and HealthCheckUseCase handlers)
- `backend/app/application/services.py` (Application service helpers placeholder)
- `backend/app/infrastructure/database/models.py` (SQLAlchemy async models mapping schema tables)
- `backend/app/infrastructure/database/unit_of_work.py` (SQLAlchemy async transaction context boundary)
- `backend/app/infrastructure/repositories/base.py` (Generic SQLAlchemy repository helper)
- `backend/app/infrastructure/repositories/candidate.py` (Async candidate database query operations)
- `backend/app/infrastructure/repositories/job.py` (Async job database query operations)
- `backend/app/infrastructure/repositories/application.py` (Async application database query)
- `backend/app/infrastructure/redis/event_bus.py` (Redis EventBus adapter client)
- `backend/app/infrastructure/config/yaml_loader.py` (Pydantic YAML loaders parsing local profiles)
- `backend/app/infrastructure/browser_client.py` (Playwright installation check helper)
- `backend/app/infrastructure/llm_client.py` (OpenRouter API key presence verification verifier)
- `backend/app/infrastructure/providers/dependencies.py` (FastAPI Depends dependency providers)

### Files Modified
- `backend/app/presentation/routes.py` (Updated health check endpoint, added config validation route with tags)

### Breaking Changes
None.

### Migrations Needed
Alembic migration `001_initial_schema` must be executed to register database tables.

### Rollback Steps
- To discard branch changes, switch to main: `git checkout main` and delete the branch: `git branch -D sprint-1.2`.

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
