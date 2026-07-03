import pytest
import uuid
from app.infrastructure.database.models import CandidateModel, JobModel, ApplicationModel
from app.infrastructure.repositories.candidate import SQLAlchemyCandidateRepository
from app.infrastructure.repositories.job import SQLAlchemyJobRepository
from app.infrastructure.repositories.application import SQLAlchemyApplicationRepository
from app.infrastructure.database import AsyncSessionLocal

pytestmark = pytest.mark.asyncio

@pytest.fixture
async def db_session():
    async with AsyncSessionLocal() as session:
        yield session
        await session.rollback()

async def test_candidate_repository_crud(db_session):
    repo = SQLAlchemyCandidateRepository(db_session)
    
    # Create candidate
    candidate_id = uuid.uuid4()
    candidate = CandidateModel(
        id=candidate_id,
        full_name="Althaf Hussain Syed",
        email=f"althaf_{uuid.uuid4().hex[:6]}@example.com",
        phone="+918376543210",
        profile_url="https://linkedin.com/in/althaf"
    )
    saved = await repo.save(candidate)
    assert saved.id == candidate_id
    
    # Read by ID
    fetched = await repo.get_by_id(candidate_id)
    assert fetched is not None
    assert fetched.full_name == "Althaf Hussain Syed"
    
    # Read by email
    fetched_email = await repo.get_by_email(candidate.email)
    assert fetched_email is not None
    assert fetched_email.id == candidate_id
    
    # Update candidate
    fetched.full_name = "Althaf H. Syed"
    await repo.save(fetched)
    updated = await repo.get_by_id(candidate_id)
    assert updated.full_name == "Althaf H. Syed"
    
    # Delete candidate
    await repo.delete(candidate_id)
    deleted = await repo.get_by_id(candidate_id)
    assert deleted is None

async def test_job_repository_crud(db_session):
    repo = SQLAlchemyJobRepository(db_session)
    
    # Create job
    job_id = uuid.uuid4()
    job = JobModel(
        id=job_id,
        company_name="Google",
        job_title="Software Engineer",
        job_description="Coding high performance agents.",
        status="unprocessed"
    )
    saved = await repo.save(job)
    assert saved.id == job_id
    
    # Read job
    fetched = await repo.get_by_id(job_id)
    assert fetched is not None
    assert fetched.company_name == "Google"
    
    # Delete job
    await repo.delete(job_id)
    deleted = await repo.get_by_id(job_id)
    assert deleted is None
