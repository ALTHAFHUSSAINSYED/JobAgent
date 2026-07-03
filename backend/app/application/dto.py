from pydantic import BaseModel, Field
from typing import Dict, Any, Optional

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
