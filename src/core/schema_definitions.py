"""
Pydantic schema definitions for the Client Activation Engine.

This module contains all data models used throughout the application,
ensuring type safety and validation consistency.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator

from .enums import (
    ClientTier,
    AssetType,
    MissingInfoCategory,
    ProcessingStatus,
)


class BaseSchema(BaseModel):
    """Base schema with common fields for all models."""
    id: UUID = Field(default_factory=uuid4)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime | None = None

    class Config:
        use_enum_values = True
        validate_assignment = True


class ClientInfo(BaseSchema):
    """Client information and configuration."""
    name: str = Field(..., description="Client name or company")
    tier: ClientTier = Field(..., description="Service tier level")
    contact_email: str = Field(..., description="Primary contact email")
    contact_name: str | None = Field(None, description="Contact person name")
    notes: str | None = Field(None, description="Additional client notes")
    
    @field_validator("contact_email")
    @classmethod
    def validate_email(cls, v: str) -> str:
        """Basic email validation."""
        if "@" not in v or "." not in v.split("@")[-1]:
            msg = "Invalid email format"
            raise ValueError(msg)
        return v.lower()


class IntakeSchema(BaseSchema):
    """Raw client intake data from various sources."""
    client_id: UUID | None = Field(None, description="Associated client ID")
    source_type: str = Field(..., description="Source of intake (email, form, dm, etc.)")
    raw_content: str = Field(..., description="Raw unprocessed content")
    attachments: list[str] = Field(default_factory=list, description="Attachment file paths")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    processing_status: ProcessingStatus = Field(default=ProcessingStatus.PENDING)


class RequirementItem(BaseModel):
    """Individual requirement extracted from intake."""
    category: str = Field(..., description="Requirement category")
    description: str = Field(..., description="Requirement description")
    priority: str = Field(default="medium", description="Priority level (low/medium/high)")
    confidence: float = Field(default=0.5, ge=0.0, le=1.0, description="Extraction confidence")
    source_reference: str | None = Field(None, description="Reference to source text")


class RequirementsSchema(BaseSchema):
    """Structured requirements extracted from intake."""
    client_id: UUID = Field(..., description="Associated client ID")
    intake_id: UUID = Field(..., description="Source intake ID")
    requirements: list[RequirementItem] = Field(default_factory=list)
    functional_requirements: list[str] = Field(default_factory=list)
    technical_requirements: list[str] = Field(default_factory=list)
    business_logic: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    assumptions: list[str] = Field(default_factory=list)


class MissingInfoItem(BaseModel):
    """Individual missing information item."""
    category: MissingInfoCategory = Field(..., description="Category of missing info")
    description: str = Field(..., description="What information is missing")
    importance: str = Field(default="medium", description="Importance level")
    suggested_questions: list[str] = Field(default_factory=list)


class MissingInfoSchema(BaseSchema):
    """Missing information analysis results."""
    client_id: UUID = Field(..., description="Associated client ID")
    requirements_id: UUID = Field(..., description="Source requirements ID")
    missing_items: list[MissingInfoItem] = Field(default_factory=list)
    completeness_score: float = Field(default=0.0, ge=0.0, le=1.0)
    blocking_items: list[str] = Field(default_factory=list)
    optional_items: list[str] = Field(default_factory=list)


class AssetSpec(BaseModel):
    """Specification for a generated asset."""
    name: str = Field(..., description="Asset name")
    type: AssetType = Field(..., description="Asset type")
    description: str = Field(..., description="Asset description")
    template: str | None = Field(None, description="Template to use")
    parameters: dict[str, Any] = Field(default_factory=dict)
    dependencies: list[str] = Field(default_factory=list)


class GenerationTaskSchema(BaseSchema):
    """Task for asset generation."""
    client_id: UUID = Field(..., description="Associated client ID")
    requirements_id: UUID = Field(..., description="Source requirements ID")
    assets: list[AssetSpec] = Field(default_factory=list)
    output_path: str = Field(..., description="Output directory path")
    generation_config: dict[str, Any] = Field(default_factory=dict)
    status: ProcessingStatus = Field(default=ProcessingStatus.PENDING)


class ValidationResult(BaseModel):
    """Result of data validation."""
    is_valid: bool = Field(..., description="Whether validation passed")
    errors: list[str] = Field(default_factory=list)
    warnings: list[str] = Field(default_factory=list)
    score: float | None = Field(None, ge=0.0, le=1.0, description="Validation score")


class WorkflowStep(BaseModel):
    """Individual step in a workflow."""
    name: str = Field(..., description="Step name")
    tool: str = Field(..., description="Tool to execute")
    parameters: dict[str, Any] = Field(default_factory=dict)
    dependencies: list[str] = Field(default_factory=list)
    timeout: int | None = Field(None, description="Timeout in seconds")


class OrchestrationWorkflow(BaseSchema):
    """Complete orchestration workflow definition."""
    client_id: UUID = Field(..., description="Associated client ID")
    name: str = Field(..., description="Workflow name")
    steps: list[WorkflowStep] = Field(default_factory=list)
    current_step: int | None = Field(None, description="Current step index")
    status: ProcessingStatus = Field(default=ProcessingStatus.PENDING)
    results: dict[str, Any] = Field(default_factory=dict)
    error_log: list[str] = Field(default_factory=list)
