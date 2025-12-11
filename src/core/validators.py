"""
Validation helpers for the Client Activation Engine.

This module provides utilities for validating schemas, serializing data,
and populating default values across different components.
"""

from typing import Any
from uuid import UUID

from pydantic import ValidationError

from .enums import ClientTier, ValidationLevel
from .schema_definitions import (
    BaseSchema,
    ClientInfo,
    IntakeSchema,
    RequirementsSchema,
    ValidationResult,
)


def validate_schema(data: dict[str, Any], schema_class: type[BaseSchema]) -> ValidationResult:
    """
    Validate data against a schema and return validation results.
    
    Args:
        data: Dictionary containing data to validate
        schema_class: Pydantic schema class to validate against
        
    Returns:
        ValidationResult with validation status and any errors
    """
    errors = []
    warnings = []
    is_valid = True
    
    try:
        schema_class(**data)
    except ValidationError as e:
        is_valid = False
        errors = [str(error) for error in e.errors()]
    
    return ValidationResult(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        score=1.0 if is_valid else 0.0,
    )


def populate_client_defaults(client_data: dict[str, Any]) -> dict[str, Any]:
    """
    Populate default values for client information.
    
    Args:
        client_data: Raw client data dictionary
        
    Returns:
        Client data with defaults populated
    """
    defaults = {
        "tier": ClientTier.STARTER.value,
        "notes": "",
    }
    
    # Merge defaults with provided data, giving priority to provided values
    return {**defaults, **client_data}


def validate_client_tier_limits(tier: ClientTier, requested_assets: int) -> ValidationResult:
    """
    Validate that requested assets don't exceed tier limits.
    
    Args:
        tier: Client tier level
        requested_assets: Number of assets requested
        
    Returns:
        ValidationResult indicating if within limits
    """
    tier_limits = {
        ClientTier.STARTER: 5,
        ClientTier.BUSINESS: 20,
        ClientTier.PREMIUM: 100,
    }
    
    max_assets = tier_limits.get(tier, 0)
    is_valid = requested_assets <= max_assets
    
    errors = []
    if not is_valid:
        errors.append(
            f"Requested {requested_assets} assets exceeds {tier.value} tier limit of {max_assets}"
        )
    
    return ValidationResult(
        is_valid=is_valid,
        errors=errors,
        warnings=[],
        score=1.0 if is_valid else 0.0,
    )


def serialize_for_storage(schema_instance: BaseSchema) -> dict[str, Any]:
    """
    Serialize schema instance for storage, handling special types.
    
    Args:
        schema_instance: Pydantic schema instance
        
    Returns:
        Dictionary suitable for JSON storage
    """
    data = schema_instance.model_dump()
    
    # Convert UUID objects to strings for JSON serialization
    def convert_uuids(obj: Any) -> Any:
        if isinstance(obj, UUID):
            return str(obj)
        elif isinstance(obj, dict):
            return {key: convert_uuids(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [convert_uuids(item) for item in obj]
        return obj
    
    return convert_uuids(data)


def validate_intake_completeness(intake: IntakeSchema) -> ValidationResult:
    """
    Validate completeness of intake data.
    
    Args:
        intake: Intake schema instance
        
    Returns:
        ValidationResult with completeness assessment
    """
    errors = []
    warnings = []
    score = 0.0
    
    # Check required fields
    if not intake.raw_content.strip():
        errors.append("Raw content cannot be empty")
    else:
        score += 0.4
    
    if not intake.source_type:
        errors.append("Source type must be specified")
    else:
        score += 0.2
    
    # Check optional but recommended fields
    if not intake.client_id:
        warnings.append("No client ID associated with intake")
    else:
        score += 0.2
    
    if not intake.attachments:
        warnings.append("No attachments provided")
    else:
        score += 0.1
    
    if not intake.metadata:
        warnings.append("No metadata provided")
    else:
        score += 0.1
    
    is_valid = len(errors) == 0
    
    return ValidationResult(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        score=min(score, 1.0),
    )


def get_validation_level_threshold(level: ValidationLevel) -> float:
    """
    Get the score threshold for a validation level.
    
    Args:
        level: Validation strictness level
        
    Returns:
        Minimum score threshold (0.0 to 1.0)
    """
    thresholds = {
        ValidationLevel.STRICT: 0.9,
        ValidationLevel.MODERATE: 0.7,
        ValidationLevel.LENIENT: 0.5,
    }
    
    return thresholds.get(level, 0.7)
