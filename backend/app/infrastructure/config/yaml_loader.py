import os
import yaml
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

from app.domain.exceptions import ConfigurationError

class PersonalInfo(BaseModel):
    full_name: str
    gender: str
    date_of_birth: str
    nationality: str
    marital_status: str

class ContactEmail(BaseModel):
    primary: str
    alternate: Optional[str] = None

class ContactPhone(BaseModel):
    country: str
    country_code: str
    number: str
    full: str

class ContactInfo(BaseModel):
    email: ContactEmail
    phone: ContactPhone
    whatsapp: Optional[Dict[str, Any]] = None

class ProfileConfig(BaseModel):
    version: str = "1.0"
    personal: PersonalInfo
    contact: ContactInfo
    profiles: Dict[str, str] = Field(default_factory=dict)
    career: Dict[str, Any] = Field(default_factory=dict)
    salary: Dict[str, Any] = Field(default_factory=dict)

class AnswersConfig(BaseModel):
    authorized_to_work_in_india: str
    government_employee: str
    military_service: str
    visa_sponsorship_required: str
    immediate_joiner: str
    relocate: str
    travel: str
    night_shift: Optional[str] = None
    rotational_shift: Optional[str] = None
    weekend_support: Optional[str] = None

class CompaniesConfig(BaseModel):
    blacklist: List[str] = Field(default_factory=list)
    whitelist: List[str] = Field(default_factory=list)

class YAMLConfigLoader:
    def __init__(self, config_dir: str = "config"):
        self.config_dir = config_dir

    def _load_yaml(self, filename: str) -> Dict[str, Any]:
        path = os.path.join(self.config_dir, filename)
        if not os.path.exists(path):
            raise ConfigurationError(f"Configuration file {path} not found.")
        try:
            with open(path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            raise ConfigurationError(f"Failed to parse YAML file {path}: {e}")

    def validate_profile(self) -> bool:
        data = self._load_yaml("profile.yaml")
        try:
            ProfileConfig.model_validate(data)
            return True
        except Exception as e:
            raise ConfigurationError(f"Invalid profile.yaml schema: {e}")

    def validate_answers(self) -> bool:
        data = self._load_yaml("answers.yaml")
        try:
            AnswersConfig.model_validate(data)
            return True
        except Exception as e:
            raise ConfigurationError(f"Invalid answers.yaml schema: {e}")

    def validate_companies(self) -> bool:
        data = self._load_yaml("companies.yaml")
        try:
            CompaniesConfig.model_validate(data)
            return True
        except Exception as e:
            raise ConfigurationError(f"Invalid companies.yaml schema: {e}")
