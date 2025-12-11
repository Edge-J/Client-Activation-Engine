"""
Code generation tool for creating project assets.

This tool generates code templates, documentation, and other project
deliverables based on extracted requirements.
"""

from typing import Any

from ...core.enums import ProcessingStatus, AssetType
from ...core.schema_definitions import ValidationResult


def get_tool_metadata() -> dict[str, Any]:
    """
    Get metadata for the code generation tool.
    
    Returns:
        Tool metadata including name, description, and parameters schema
    """
    return {
        "name": "generate_code",
        "description": "Generate code and documentation based on requirements",
        "version": "1.0.0", 
        "category": "generation",
        "parameters": {
            "type": "object",
            "properties": {
                "requirements": {
                    "type": "object",
                    "description": "Extracted requirements from analysis phase",
                },
                "asset_type": {
                    "type": "string",
                    "description": "Type of asset to generate",
                    "enum": ["code", "documentation", "configuration", "template"],
                },
                "technology_stack": {
                    "type": "object", 
                    "description": "Technology preferences and constraints",
                },
                "output_config": {
                    "type": "object",
                    "description": "Output configuration and preferences",
                },
            },
            "required": ["requirements", "asset_type"],
        },
        "returns": {
            "type": "object",
            "description": "Generated asset content and metadata",
        },
    }


async def run(
    requirements: dict[str, Any],
    asset_type: str,
    technology_stack: dict[str, Any] | None = None,
    output_config: dict[str, Any] | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """
    Generate code and documentation based on requirements.
    
    Args:
        requirements: Extracted requirements from analysis phase
        asset_type: Type of asset to generate
        technology_stack: Technology preferences and constraints
        output_config: Output configuration and preferences
        **kwargs: Additional parameters
        
    Returns:
        Dictionary containing generated asset content and metadata
        
    Raises:
        ValueError: If input parameters are invalid
        RuntimeError: If generation fails
    """
    # Validate inputs
    if not requirements or not isinstance(requirements, dict):
        msg = "Invalid requirements data"
        raise ValueError(msg)
    
    valid_types = ["code", "documentation", "configuration", "template"]
    if asset_type not in valid_types:
        msg = f"Invalid asset type: {asset_type}. Must be one of {valid_types}"
        raise ValueError(msg)
    
    # TODO: Implement LLM-based code generation
    # This is a placeholder implementation
    
    # Mock generation based on asset type
    if asset_type == "code":
        generated_content = _generate_mock_code(requirements, technology_stack)
    elif asset_type == "documentation":
        generated_content = _generate_mock_documentation(requirements)
    elif asset_type == "configuration":
        generated_content = _generate_mock_configuration(requirements)
    else:  # template
        generated_content = _generate_mock_template(requirements)
    
    return {
        "status": ProcessingStatus.COMPLETED.value,
        "asset_type": asset_type,
        "content": generated_content,
        "metadata": {
            "requirements_count": len(requirements.get("functional_requirements", [])),
            "technology_stack": technology_stack or {},
            "output_config": output_config or {},
            "generation_timestamp": "2024-03-15T10:30:00Z",
        },
        "quality_metrics": {
            "completeness_score": 0.8,
            "code_quality_score": 0.85,
            "documentation_coverage": 0.9,
        },
        "processing_notes": [
            "Placeholder implementation - requires LLM integration",
            f"Generated {asset_type} asset based on mock templates",
        ],
    }


def _generate_mock_code(
    requirements: dict[str, Any], 
    tech_stack: dict[str, Any] | None,
) -> dict[str, Any]:
    """Generate mock code content."""
    return {
        "files": {
            "app.py": "# Flask application template\nfrom flask import Flask\napp = Flask(__name__)",
            "models.py": "# Database models\nfrom sqlalchemy import Column, Integer, String",
            "config.py": "# Application configuration\nclass Config:\n    SECRET_KEY = 'dev-key'",
        },
        "structure": ["app.py", "models.py", "config.py", "requirements.txt"],
        "instructions": "Run 'pip install -r requirements.txt' to install dependencies",
    }


def _generate_mock_documentation(requirements: dict[str, Any]) -> dict[str, Any]:
    """Generate mock documentation content."""
    return {
        "documents": {
            "README.md": "# Project Documentation\n\nProject overview and setup instructions",
            "API.md": "# API Documentation\n\nEndpoint specifications and examples",
            "DEPLOYMENT.md": "# Deployment Guide\n\nProduction deployment instructions",
        },
        "sections": ["overview", "installation", "usage", "api", "deployment"],
        "format": "markdown",
    }


def _generate_mock_configuration(requirements: dict[str, Any]) -> dict[str, Any]:
    """Generate mock configuration content.""" 
    return {
        "configs": {
            "docker-compose.yml": "version: '3.8'\nservices:\n  web:\n    build: .",
            "nginx.conf": "server {\n  listen 80;\n  location / {\n    proxy_pass http://web:5000;\n  }\n}",
            ".env.example": "DATABASE_URL=postgresql://user:pass@localhost/db\nSECRET_KEY=your-secret-key",
        },
        "deployment_type": "docker",
        "environment": "production",
    }


def _generate_mock_template(requirements: dict[str, Any]) -> dict[str, Any]:
    """Generate mock template content."""
    return {
        "templates": {
            "base.html": "<!DOCTYPE html>\n<html>\n<head><title>{{ title }}</title></head>",
            "index.html": "{% extends 'base.html' %}\n{% block content %}Welcome{% endblock %}",
        },
        "template_engine": "jinja2",
        "static_files": ["css/style.css", "js/app.js"],
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
    if "requirements" not in parameters:
        errors.append("Missing required parameter: requirements")
    elif not isinstance(parameters["requirements"], dict):
        errors.append("Parameter 'requirements' must be a dictionary")
    
    if "asset_type" not in parameters:
        errors.append("Missing required parameter: asset_type")
    else:
        valid_types = ["code", "documentation", "configuration", "template"]
        if parameters["asset_type"] not in valid_types:
            errors.append(f"Invalid asset_type. Must be one of: {valid_types}")
    
    # Validate optional parameters
    if "technology_stack" in parameters and not isinstance(parameters["technology_stack"], dict):
        warnings.append("Parameter 'technology_stack' should be a dictionary")
    
    if "output_config" in parameters and not isinstance(parameters["output_config"], dict):
        warnings.append("Parameter 'output_config' should be a dictionary")
    
    is_valid = len(errors) == 0
    score = 1.0 if is_valid else 0.0
    
    return ValidationResult(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        score=score,
    )
