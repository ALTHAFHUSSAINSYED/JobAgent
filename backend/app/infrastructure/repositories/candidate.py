from typing import Optional
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.interfaces import ICandidateRepository
from app.infrastructure.repositories.base import SQLAlchemyBaseRepository
from app.infrastructure.database.models import CandidateModel

class SQLAlchemyCandidateRepository(SQLAlchemyBaseRepository[CandidateModel], ICandidateRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session, CandidateModel)

    async def get_by_email(self, email: str) -> Optional[CandidateModel]:
        result = await self.session.execute(select(CandidateModel).filter_by(email=email))
        return result.scalar_one_or_none()
