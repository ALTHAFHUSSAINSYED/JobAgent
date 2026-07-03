from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List

class HealthStatusDTO(BaseModel):
    status: str
    database: str
    redis: str
    playwright: str
    configuration: str

class ConfigurationStatusDTO(BaseModel):
    valid: bool
    profile_loaded: bool
    answers_loaded: bool
    companies_loaded: bool
    errors: Optional[str] = None

class SystemInfoDTO(BaseModel):
    python_version: str
    docker_status: str
    postgres_version: str
    redis_version: str
    playwright_version: str
    git_branch: str
    git_commit: str

class ConfigDetailDTO(BaseModel):
    expected_ctc: str
    preferred_locations: List[str]
    immediate_joiner: bool
    experience_years: float
    skills_count: int
    skills_list: List[str]

class DashboardDTO(BaseModel):
    health: HealthStatusDTO
    jobs_count: int
    applications_count: int
    resume_status: Dict[str, Any]
    configuration: ConfigDetailDTO

class VersionDTO(BaseModel):
    version: str
    build_date: str
    commit: str
