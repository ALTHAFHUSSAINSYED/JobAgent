from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.interfaces import IJobRepository
from app.infrastructure.repositories.base import SQLAlchemyBaseRepository
from app.infrastructure.database.models import JobModel

class SQLAlchemyJobRepository(SQLAlchemyBaseRepository[JobModel], IJobRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, JobModel)
