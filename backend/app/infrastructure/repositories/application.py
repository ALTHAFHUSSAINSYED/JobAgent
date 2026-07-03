from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.interfaces import IApplicationRepository
from app.infrastructure.repositories.base import SQLAlchemyBaseRepository
from app.infrastructure.database.models import ApplicationModel

class SQLAlchemyApplicationRepository(SQLAlchemyBaseRepository[ApplicationModel], IApplicationRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, ApplicationModel)
