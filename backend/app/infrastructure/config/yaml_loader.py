import os
import re
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

def check_placeholders(data: Any, path: str = "") -> None:
    """Recursively checks for bracketed unpopulated placeholders like <FULL_NAME>."""
    if isinstance(data, str):
        if data.startswith("<") and data.endswith(">"):
            raise ConfigurationError(f"Found unpopulated placeholder '{data}' at path '{path}'")
    elif isinstance(data, dict):
        for k, v in data.items():
            check_placeholders(v, f"{path}.{k}" if path else k)
    elif isinstance(data, list):
        for idx, item in enumerate(data):
            check_placeholders(item, f"{path}[{idx}]")

def parse_experience_years(exp: Any) -> float:
    """Parses experience strings (e.g. 3y10m or 3.1) into float years."""
    if exp is None:
        return 0.0
    if isinstance(exp, (int, float)):
        return float(exp)
    if isinstance(exp, str):
        exp_str = exp.strip().lower()
        # Parse formats like "3y10m"
        m = re.match(r'^(?:(\d+)y)?\s*(?:(\d+)m)?$', exp_str)
        if m:
            years = int(m.group(1)) if m.group(1) else 0
            months = int(m.group(2)) if m.group(2) else 0
            return round(years + (months / 12.0), 2)
        # Parse standard numbers
        try:
            return float(exp_str)
        except ValueError:
            pass
    raise ConfigurationError(f"Unable to parse experience string format: {exp}")

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
            check_placeholders(data)
            return True
        except Exception as e:
            raise ConfigurationError(f"Profile config validation failed: {e}")

    def validate_answers(self) -> bool:
        data = self._load_yaml("answers.yaml")
        try:
            AnswersConfig.model_validate(data)
            check_placeholders(data)
            return True
        except Exception as e:
            raise ConfigurationError(f"Answers config validation failed: {e}")

    def validate_companies(self) -> bool:
        data = self._load_yaml("companies.yaml")
        try:
            CompaniesConfig.model_validate(data)
            check_placeholders(data)
            return True
        except Exception as e:
            raise ConfigurationError(f"Companies config validation failed: {e}")
