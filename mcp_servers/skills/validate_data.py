"""
Data validation skill for verifying and sanitizing data.

This skill provides reusable validation capabilities that can be
used across different workflow steps.
"""

from typing import Any

from ...core.enums import ValidationLevel
from ...core.schema_definitions import ValidationResult


def get_tool_metadata() -> dict[str, Any]:
    """
    Get metadata for the data validation skill.
    
    Returns:
        Tool metadata including name, description, and parameters schema
    """
    return {
        "name": "validate_data",
        "description": "Validate and sanitize data according to specified rules",
        "version": "1.0.0",
        "category": "skills",
        "parameters": {
            "type": "object",
            "properties": {
                "data": {
                    "type": "object",
                    "description": "Data to validate",
                },
                "validation_rules": {
                    "type": "object",
                    "description": "Validation rules and constraints",
                },
                "validation_level": {
                    "type": "string",
                    "description": "Validation strictness level",
                    "enum": ["strict", "moderate", "lenient"],
                    "default": "moderate",
                },
            },
            "required": ["data", "validation_rules"],
        },
        "returns": {
            "type": "object",
            "description": "Validation results and sanitized data",
        },
    }


async def run(parameters: dict[str, Any]) -> dict[str, Any]:
    """
    Validate and sanitize data according to specified rules.
    
    Args:
        parameters: Tool execution parameters containing:
            - data: Data to validate
            - validation_rules: Validation rules and constraints  
            - validation_level: Validation strictness level (optional, default: "moderate")
        
    Returns:
        Dictionary containing validation results and sanitized data
        
    Raises:
        ValueError: If input parameters are invalid
    """
    # Unpack parameters from the input dictionary
    data = parameters.get("data", {})
    validation_rules = parameters.get("validation_rules", {})
    validation_level = parameters.get("validation_level", "moderate")
    
    # Validate inputs
    if not isinstance(data, dict):
        msg = "Data must be a dictionary"
        raise ValueError(msg)
    
    if not isinstance(validation_rules, dict):
        msg = "Validation rules must be a dictionary"
        raise ValueError(msg)
    
    valid_levels = ["strict", "moderate", "lenient"]
    if validation_level not in valid_levels:
        msg = f"Invalid validation level: {validation_level}"
        raise ValueError(msg)
    
    # TODO: Implement comprehensive data validation
    # This is a placeholder implementation
    
    errors = []
    warnings = []
    sanitized_data = data.copy()
    
    # Mock validation logic
    for field, rules in validation_rules.items():
        if field not in data:
            if rules.get("required", False):
                errors.append(f"Required field missing: {field}")
            continue
            
        value = data[field]
        field_type = rules.get("type")
        
        # Type validation
        if field_type == "string" and not isinstance(value, str):
            if validation_level == "strict":
                errors.append(f"Field {field} must be a string")
            else:
                sanitized_data[field] = str(value)
                warnings.append(f"Field {field} converted to string")
        
        # Length validation
        if isinstance(value, str) and "max_length" in rules:
            max_len = rules["max_length"]
            if len(value) > max_len:
                if validation_level == "strict":
                    errors.append(f"Field {field} exceeds max length {max_len}")
                else:
                    sanitized_data[field] = value[:max_len]
                    warnings.append(f"Field {field} truncated to {max_len} characters")
    
    # Calculate validation score
    total_checks = len(validation_rules)
    failed_checks = len(errors)
    score = max(0.0, (total_checks - failed_checks) / max(total_checks, 1))
    
    is_valid = len(errors) == 0
    
    return {
        "validation_result": ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            score=score,
        ).model_dump(),
        "sanitized_data": sanitized_data,
        "validation_metadata": {
            "level": validation_level,
            "rules_applied": len(validation_rules),
            "fields_processed": len(data),
            "errors_found": len(errors),
            "warnings_issued": len(warnings),
        },
        "processing_notes": [
            "Placeholder implementation - basic validation logic only",
            f"Applied {validation_level} validation to {len(data)} fields",
        ],
    }


def validate_parameters(parameters: dict[str, Any]) -> ValidationResult:
    """
    Validate tool parameters before execution.
    
    Args:
        parameters: Tool parameters to validate
        
    Returns:
        ValidationResult with validation status and any errors
    """
    errors = []
    warnings = []
    
    # Check required parameters
    if "data" not in parameters:
        errors.append("Missing required parameter: data")
    elif not isinstance(parameters["data"], dict):
        errors.append("Parameter 'data' must be a dictionary")
    
    if "validation_rules" not in parameters:
        errors.append("Missing required parameter: validation_rules")
    elif not isinstance(parameters["validation_rules"], dict):
        errors.append("Parameter 'validation_rules' must be a dictionary")
    
    # Validate optional parameters
    if "validation_level" in parameters:
        valid_levels = ["strict", "moderate", "lenient"]
        if parameters["validation_level"] not in valid_levels:
            errors.append(f"Invalid validation_level. Must be one of: {valid_levels}")
    
    is_valid = len(errors) == 0
    score = 1.0 if is_valid else 0.0
    
    return ValidationResult(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        score=score,
    )
