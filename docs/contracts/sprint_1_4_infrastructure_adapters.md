# Sprint 1.4: Infrastructure Adapters & API Gateways

This contract specifies the adapter interfaces, generic repositories, pub/sub configurations, and config profile validations for JobPilot AI.

---

## 1. Goal
Decouple external systems (database, Redis, Playwright, LLMs, YAML configurations) from business logic through abstract interfaces and generic database classes.

---

## 2. Directory Layout & Key Files
```text
backend/app/
├── domain/
│   └── interfaces.py        # Abstract repository and EventBus contracts
└── infrastructure/
    ├── repositories.py      # Async generic DB base & concrete repositories
    ├── event_bus.py         # Redis Pub/Sub EventBus implementation
    ├── config_parser.py     # Pydantic schemas validating YAML inputs
    ├── browser_client.py    # Playwright verification client
    └── llm_client.py        # OpenRouter credential API check
```

---

## 3. Specifications

### 3.1 Generic Async Repository Pattern
We must build a generic repository base to avoid boilerplate CRUD code:

```python
# backend/app/domain/interfaces.py
from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional
from uuid import UUID

T = TypeVar('T')

class IRepository(ABC, Generic[T]):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[T]: pass
    @abstractmethod
    async def list(self) -> List[T]: pass
    @abstractmethod
    async def save(self, entity: T) -> T: pass
    @abstractmethod
    async def delete(self, id: UUID) -> None: pass
```

```python
# backend/app/infrastructure/repositories.py
from typing import Generic, TypeVar, List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.domain.interfaces import IRepository

ModelType = TypeVar('ModelType')

class SQLAlchemyBaseRepository(IRepository[ModelType], Generic[ModelType]):
    def __init__(self, session: AsyncSession, model: ModelType):
        self.session = session
        self.model = model

    async def get_by_id(self, id: UUID) -> Optional[ModelType]:
        result = await self.session.execute(select(self.model).filter_by(id=id))
        return result.scalar_one_or_none()

    async def list(self) -> List[ModelType]:
        result = await self.session.execute(select(self.model))
        return list(result.scalars().all())

    async def save(self, entity: ModelType) -> ModelType:
        self.session.add(entity)
        await self.session.commit()
        await self.session.refresh(entity)
        return entity

    async def delete(self, id: UUID) -> None:
        entity = await self.get_by_id(id)
        if entity:
            await self.session.delete(entity)
            await self.session.commit()
```

### 3.2 Redis Event Bus Adapter
Decouple the application from Redis. The application uses `IEventBus`.
- **Implementation:** `RedisEventBus` implements `IEventBus` using async redis.
- **Queue/Channel Handling:** Publishes JSON strings to Redis channels, listens in an async loop for subscriptions.

### 3.3 Verification Clients
- **Playwright Verifier:** Checks if Playwright is installed and executable path for chromium exists.
- **OpenRouter Verifier:** Validates that the `OPENROUTER_API_KEY` exists and pings OpenRouter's profile endpoint to verify key validity.

### 3.4 Config YAML Parsers
- Check configurations inside `config/` directory.
- Expose schemas: `ProfileConfigSchema`, `AnswersConfigSchema`, `CompaniesConfigSchema`.

---

## 4. Acceptance Criteria
- Configuration validator correctly flags malformed YAML inputs.
- `RedisEventBus` can publish and receive messages over Redis.
- Playwright and OpenRouter checkers correctly return diagnostic status strings.
