from abc import ABC, abstractmethod
from typing import Generic, TypeVar, List, Optional, Any, Dict
from uuid import UUID

T = TypeVar('T')

class IRepository(ABC, Generic[T]):
    @abstractmethod
    async def get_by_id(self, id: UUID) -> Optional[T]:
        """Fetch entity by unique identifier."""
        pass

    @abstractmethod
    async def list(self) -> List[T]:
        """Fetch all stored entities."""
        pass

    @abstractmethod
    async def save(self, entity: T) -> T:
        """Persist or update entity state."""
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> None:
        """Remove entity from database."""
        pass

class ICandidateRepository(IRepository[Any], ABC):
    @abstractmethod
    async def get_by_email(self, email: str) -> Optional[Any]:
        """Fetch candidate details by email address."""
        pass

class IJobRepository(IRepository[Any], ABC):
    pass

class IApplicationRepository(IRepository[Any], ABC):
    pass

class IUnitOfWork(ABC):
    @abstractmethod
    async def __aenter__(self) -> 'IUnitOfWork':
        pass

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    @abstractmethod
    async def commit(self) -> None:
        """Commit transaction."""
        pass

    @abstractmethod
    async def rollback(self) -> None:
        """Rollback transaction."""
        pass

class IEventBus(ABC):
    @abstractmethod
    async def publish(self, event_name: str, payload: Dict[str, Any]) -> None:
        """Publish event notification payload."""
        pass

    @abstractmethod
    async def subscribe(self, event_name: str, handler: Any) -> None:
        """Subscribe handler function to channel alerts."""
        pass

class IJobProvider(ABC):
    @abstractmethod
    async def search(self, query: str) -> List[Any]:
        """Discovers new jobs for a target role query."""
        pass

    @abstractmethod
    async def fetch(self, url: str) -> Any:
        """Fetches full details of a specific job posting."""
        pass

