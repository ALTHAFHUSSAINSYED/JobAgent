# Sprint 1.2: Backend Core & Async Database Integration

This contract specifies the core application setup, tracing middleware, and asynchronous database layer for JobPilot AI.

---

## 1. Goal
Initialize the FastAPI application, set up correlation ID tracking middleware, configure structural logging mapping correlation IDs to execution logs, configure async database interfaces (SQLAlchemy + asyncpg), and set up Alembic migrations.

---

## 2. Directory Layout & Key Files
```text
backend/app/
├── main.py                  # Server bootstrap & lifecycles
├── core/
│   ├── config.py            # Settings engine (Pydantic Settings v2)
│   ├── logging.py           # Structlog / logging handlers setup
│   └── correlation.py       # Correlation ID ContextVar middleware
└── infrastructure/
    └── database.py          # Async engine, sessionmaker, and base model
```

---

## 3. Specifications

### 3.1 Correlation ID Tracking Middleware
Every request entering the FastAPI server must be assigned a unique `Correlation ID` (stored in a thread-safe `contextvars.ContextVar`).
- **Header:** `X-Correlation-ID`
- **Behavior:**
  - If the client sends an `X-Correlation-ID` header, read it.
  - If not, generate a new `uuid.uuid4()`.
  - Attach the Correlation ID to the incoming request context.
  - Inject the `X-Correlation-ID` header into the response.

### 3.2 Structured Logging
The logging system must pull the active correlation ID from the context variable and inject it into all log statements.
- **Log Format:** `[%(asctime)s] [%(levelname)s] [CorrID: %(correlation_id)s] [%(name)s:%(lineno)d] - %(message)s`

### 3.3 Asynchronous Database Setup (SQLAlchemy 2.0 + asyncpg)
We must run SQLAlchemy in complete asynchronous execution mode.

```python
# backend/app/infrastructure/database.py
import contextlib
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base

from app.core.config import settings

# Async engine configured for postgresql+asyncpg
async_engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    pool_pre_ping=True,
    future=True
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

Base = declarative_base()

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency generator for database sessions in FastAPI routes."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
```

### 3.4 Alembic Async Config
- Alembic must be initialized with the `async` template:
  `alembic init -t async alembic`
- In `alembic/env.py`, modify target metadata to bind to the async engine.
- Configure `sqlalchemy.url` to run with `postgresql+asyncpg`.

---

## 4. Acceptance Criteria
- Starting the backend exposes `/docs` (Swagger UI).
- Sending requests to backend returns an `X-Correlation-ID` header in the response.
- Server stdout prints logs containing the `[CorrID: <uuid>]` tag.
- Alembic database migration creates PostgreSQL tables using async schemas successfully.
