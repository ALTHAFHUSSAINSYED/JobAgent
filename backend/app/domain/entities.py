from dataclasses import dataclass, field
from datetime import datetime, timezone
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
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class Job:
    company_name: str
    job_title: str
    job_description: str
    portal: str
    apply_url: str
    location: Optional[str] = None
    remote: bool = False
    salary: Optional[str] = None
    experience: Optional[str] = None
    skills: Optional[str] = None
    posted_date: Optional[datetime] = None
    scraped_date: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    employment_type: Optional[str] = None
    work_mode: Optional[str] = None
    source_hash: Optional[str] = None
    match_score: Optional[float] = None
    status: JobStatus = JobStatus.UNPROCESSED
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

@dataclass
class Application:
    candidate_id: UUID
    job_id: UUID
    status: ApplicationStatus = ApplicationStatus.APPLIED
    tailored_resume_path: Optional[str] = None
    submitted_payload: Optional[str] = None
    id: UUID = field(default_factory=uuid4)
    submitted_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
