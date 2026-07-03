from sqlalchemy import Column, String, Text, Numeric, ForeignKey, Boolean
from sqlalchemy import DateTime as SaDateTime
from sqlalchemy.types import TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime, timezone

from app.infrastructure.database import Base


def _utcnow() -> datetime:
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class CandidateModel(Base):
    __tablename__ = "candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), nullable=False, unique=True, index=True)
    phone = Column(String(50), nullable=True)
    profile_url = Column(String(500), nullable=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=_utcnow)


class JobModel(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    portal = Column(String(100), nullable=False, index=True)
    company_name = Column(String(255), nullable=False, index=True)
    job_title = Column(String(255), nullable=False, index=True)
    job_description = Column(Text, nullable=False)
    apply_url = Column(String(750), nullable=False)
    location = Column(String(255), nullable=True, index=True)
    remote = Column(Boolean, nullable=False, default=False, index=True)
    salary = Column(String(100), nullable=True)
    experience = Column(String(100), nullable=True)
    skills = Column(Text, nullable=True)
    posted_date = Column(TIMESTAMP(timezone=True), nullable=True)
    scraped_date = Column(TIMESTAMP(timezone=True), nullable=False, default=_utcnow)
    employment_type = Column(String(100), nullable=True)
    work_mode = Column(String(100), nullable=True, index=True)
    source_hash = Column(String(64), nullable=False, unique=True, index=True)
    match_score = Column(Numeric(5, 2), nullable=True, index=True)
    status = Column(String(50), nullable=False, default="unprocessed", index=True)
    created_at = Column(TIMESTAMP(timezone=True), nullable=False, default=_utcnow)


class ApplicationModel(Base):
    __tablename__ = "applications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    candidate_id = Column(UUID(as_uuid=True), ForeignKey("candidates.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="CASCADE"), nullable=False)
    status = Column(String(50), nullable=False, default="Applied", index=True)
    tailored_resume_path = Column(String(500), nullable=True)
    submitted_payload = Column(Text, nullable=True)
    submitted_at = Column(TIMESTAMP(timezone=True), nullable=False, default=_utcnow)
