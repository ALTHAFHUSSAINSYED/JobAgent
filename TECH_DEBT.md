# Technical Debt Registry — JobPilot AI

This document tracks identified code smells, deprecation warnings, structural shortcuts, and optimization items. It is updated at the start of each sprint to prevent technical debt from accumulating silently.

---

## 1. Active Issues & Warnings

### A. Python 3.12 `datetime.utcnow()` Deprecations
- **Description:** Pytest logs `DeprecationWarning` due to `datetime.utcnow` usage:
  `DeprecationWarning: datetime.datetime.utcnow() is deprecated and scheduled for removal in a future version.`
- **Files Affected:**
  - `backend/app/domain/entities.py` (Lines 14, 27, 37)
  - `backend/app/infrastructure/database/models.py` (Lines 16, 30, 41)
- **Refactoring Plan:** Replace with timezone-aware `datetime.now(timezone.utc)`.

### B. CI Quality Gate Enforcement Limits
- **Description:** Pytest coverage is generated in the CI workflow, but there is no threshold assertion. Code can be merged even with 0% coverage.
- **Files Affected:** `.github/workflows/ci.yml`
- **Refactoring Plan:** Set pytest arguments to enforce a minimum coverage threshold (e.g., `--cov-fail-under=60` initially, scaling to `80`).

### C. Missing Database Indices
- **Description:** Schema tables (`jobs` and `applications`) do not declare index fields. Once the Job Discovery Engine starts scraping thousands of positions, dashboard queries and duplicate detectors will query un-indexed text fields, degrading database response latencies.
- **Files Affected:** `backend/app/infrastructure/database/models.py`
- **Refactoring Plan:** Add indices on `title`, `company`, and `status`.

---

## 2. Infrastructure & Structural Shortcuts

### A. Active Configuration Watcher Polling
- **Description:** The `ConfigWatcher` uses a polling model checking `os.path.getmtime` every 2 seconds.
- **Implication:** Higher disk IO check calls.
- **Refactoring Plan:** Keep as-is for low-complexity zero-dependency cross-platform support. In later phases, migrate to `watchdog` to intercept OS-level file system signals.

### B. Resumes Path Hardcoding
- **Description:** `ResumeManager` relies on hardcoded string path reference `"resumes"`.
- **Files Affected:** `backend/app/infrastructure/repositories/resume.py`
- **Refactoring Plan:** Expose resume directory paths inside Pydantic `settings` to allow clean overrides during testing.

### C. Event Bus Reconnection Resiliency
- **Description:** `RedisEventBus` establishes connections but does not implement auto-retry backoff parameters if Redis goes offline during execution.
- **Files Affected:** `backend/app/infrastructure/redis/event_bus.py`
- **Refactoring Plan:** Implement custom reconnection attempt thresholds.

---

## 3. Telemetry & Performance Optimizations

### A. Exclude Health & Sockets from Prometheus Middleware
- **Description:** High-frequency metrics queries themselves are captured by metrics middleware if not explicitly bypassed.
- **Files Affected:** `backend/app/core/metrics.py`
- **Status:** Mitigated by skipping `/metrics` pathways.

### B. Response Compression
- **Description:** Exchanged dashboard datasets can grow large as job listings expand.
- **Files Affected:** `backend/app/main.py`
- **Refactoring Plan:** Add `GZipMiddleware` to compress outgoing HTTP payloads.
