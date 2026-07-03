from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.domain.interfaces import IJobRepository
from app.infrastructure.repositories.base import SQLAlchemyBaseRepository
from app.infrastructure.database.models import JobModel

class SQLAlchemyJobRepository(SQLAlchemyBaseRepository[JobModel], IJobRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, JobModel)

    async def exists_by_hash(self, source_hash: str) -> bool:
        """Checks if a job listing already exists via its content hash."""
        stmt = select(JobModel).where(JobModel.source_hash == source_hash)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none() is not None

    async def get_by_hash(self, source_hash: str) -> Optional[JobModel]:
        """Fetches a single job model via its source content hash."""
        stmt = select(JobModel).where(JobModel.source_hash == source_hash)
        res = await self.session.execute(stmt)
        return res.scalar_one_or_none()
