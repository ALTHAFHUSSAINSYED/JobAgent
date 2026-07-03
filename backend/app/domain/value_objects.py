from enum import Enum

class ApplicationStatus(str, Enum):
    APPLIED = "Applied"
    INTERVIEW = "Interview"
    OFFER = "Offer"
    REJECTED = "Rejected"

class JobStatus(str, Enum):
    UNPROCESSED = "unprocessed"
    SKIPPED = "skipped"
    MATCHED = "matched"
    APPLYING = "applying"
    FAILED = "failed"
    SUCCESS = "success"

class InterventionType(str, Enum):
    MFA = "mfa"
    CAPTCHA = "captcha"
    QUESTIONNAIRE = "questionnaire"
