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
        await self.session.flush() # flush to assign generated fields/ID before commit
        return entity

    async def delete(self, id: UUID) -> None:
        entity = await self.get_by_id(id)
        if entity:
            await self.session.delete(entity)
            await self.session.flush()
