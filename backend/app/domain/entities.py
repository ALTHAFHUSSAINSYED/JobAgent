from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID, uuid4
from typing import Optional, List, Dict, Any
from app.domain.value_objects import ApplicationStatus, JobStatus

@dataclass
class Candidate:
    full_name: str
    email: str
    phone: Optional[str] = None
    profile_url: Optional[str] = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Job:
    company_name: str
    job_title: str
    job_description: str
    portal_id: Optional[str] = None
    portal_name: Optional[str] = None
    salary_range: Optional[str] = None
    match_score: Optional[float] = None
    status: JobStatus = JobStatus.UNPROCESSED
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.utcnow)

@dataclass
class Application:
    candidate_id: UUID
    job_id: UUID
    status: ApplicationStatus = ApplicationStatus.APPLIED
    tailored_resume_path: Optional[str] = None
    submitted_payload: Optional[str] = None
    id: UUID = field(default_factory=uuid4)
    submitted_at: datetime = field(default_factory=datetime.utcnow)
