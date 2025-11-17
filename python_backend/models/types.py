"""
Type definitions and enums
"""
from enum import Enum
from datetime import datetime
from typing import Optional, Dict, Any
from pydantic import BaseModel


# Enums
class Provider(str, Enum):
    AZURE_OPENAI = "azure_openai"
    GEMINI = "gemini"
    GEMMA = "gemma"


class ConfigStatus(str, Enum):
    DRAFT = "draft"
    TESTED = "tested"
    ACTIVE = "active"
    INACTIVE = "inactive"


class ModelPurpose(str, Enum):
    EVALUATION = "evaluation"
    VERIFICATION = "verification"


class SubmissionStatus(str, Enum):
    RECEIVED = "received"
    VALIDATED = "validated"
    QUEUED_FOR_SCORING = "queued_for_scoring"
    FAILED = "failed"


class Role(str, Enum):
    ADMIN = "admin"
    CONTRIBUTOR = "contributor"


class Permission(str, Enum):
    MODEL_CONFIG_READ = "model:read"
    MODEL_CONFIG_WRITE = "model:write"
    RUBRIC_READ = "rubric:read"
    RUBRIC_WRITE = "rubric:write"
    IDEA_SUBMIT = "idea:submit"
    IDEA_READ = "idea:read"


class ErrorCode(str, Enum):
    # CSV Errors
    CSV_HEADER_MISMATCH = "CSV_001"
    CSV_EMPTY_FILE = "CSV_002"
    CSV_TOO_MANY_ROWS = "CSV_003"
    ROW_VALIDATION_FAILED = "CSV_100"
    ROW_MISSING_REQUIRED_FIELD = "CSV_101"
    ROW_INVALID_EMAIL = "CSV_102"
    ROW_TITLE_LENGTH = "CSV_103"
    ROW_LOGLINE_LENGTH = "CSV_104"
    
    # File Errors
    FILE_TYPE_NOT_ALLOWED = "FILE_001"
    FILE_TOO_LARGE = "FILE_002"
    FILE_MIME_MISMATCH = "FILE_003"
    VIRUS_SCAN_FAILED = "FILE_004"
    FILE_UPLOAD_FAILED = "FILE_005"
    
    # Rate Limiting
    RATE_LIMITED = "RATE_001"
    
    # Configuration Errors
    CONFIG_TEST_FAILED = "CONFIG_001"
    CONFIG_INVALID_SETTINGS = "CONFIG_002"
    CONFIG_ACTIVATION_FAILED = "CONFIG_003"
    
    # Rubric Errors
    WEIGHT_TOTAL_INVALID = "RUBRIC_001"
    RUBRIC_NAME_DUPLICATE = "RUBRIC_002"
    RUBRIC_CANNOT_DELETE_DEFAULT = "RUBRIC_003"
    
    # Auth Errors
    UNAUTHORIZED = "AUTH_001"
    FORBIDDEN = "AUTH_002"


# Request Models
class ActivateConfigRequest(BaseModel):
    purpose: ModelPurpose


# Models
class ModelProviderConfig(BaseModel):
    id: str
    provider: Provider
    name: str
    is_active: bool
    settings: Dict[str, Any]
    status: ConfigStatus
    version: int
    notes: Optional[str] = None
    purpose: Optional[ModelPurpose] = None
    created_by: str
    created_at: datetime
    updated_at: datetime


class Rubric(BaseModel):
    id: str
    name: str
    description: str
    guidance: str
    scale_min: int
    scale_max: int
    weight: float
    is_default: bool
    is_active: bool
    display_order: int
    created_by: str
    created_at: datetime
    updated_at: datetime


class IdeaSubmission(BaseModel):
    id: str
    submitter_id: str
    csv_file_uri: str
    support_file_uri: Optional[str] = None
    support_file_type: Optional[str] = None
    total_rows: int
    valid_rows: int
    invalid_rows: int
    error_report_uri: Optional[str] = None
    status: SubmissionStatus
    source_ip: Optional[str] = None
    checksum: Optional[str] = None
    created_at: datetime
    processed_at: Optional[datetime] = None


class Idea(BaseModel):
    id: str
    submission_id: str
    idea_id: Optional[int] = None
    title: str
    brief_summary: str
    challenge_opportunity: Optional[str] = None
    novelty_benefits_risks: Optional[str] = None
    responsible_ai_adherence: Optional[str] = None
    additional_documentation: Optional[str] = None
    second_file_info: Optional[str] = None
    preferred_week: Optional[str] = None
    build_phase_preference: Optional[str] = None
    build_method_preference: Optional[str] = None
    code_development_preference: Optional[str] = None
    score: Optional[float] = None
    feedback: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None


class ErrorResponse(BaseModel):
    error_code: ErrorCode
    message: str
    details: Optional[Any] = None
    timestamp: str


class User(BaseModel):
    user_id: str
    email: str
    role: Role
    permissions: list[Permission]
