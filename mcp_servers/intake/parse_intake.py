"""
Intake parsing tool for processing raw client communications.

This tool extracts structured information from various types of client input
including emails, forms, direct messages, and documents.
"""

from typing import Any, Dict

from ...core.enums import ProcessingStatus
from ...core.schema_definitions import IntakeSchema, ValidationResult


def get_tool_metadata() -> Dict[str, Any]:
    """
    Get metadata for the intake parsing tool.
    
    Returns:
        Tool metadata including name, description, and parameters schema
    """
    return {
        "name": "parse_intake",
        "description": "Parse raw client input into structured format",
        "version": "1.0.0",
        "category": "intake",
        "parameters": {
            "type": "object",
            "properties": {
                "raw_content": {
                    "type": "string",
                    "description": "Raw client communication content"
                },
                "source_type": {
                    "type": "string", 
                    "description": "Type of communication source",
                    "enum": ["email", "form", "direct_message", "phone_transcript", "document"]
                },
                "metadata": {
                    "type": "object",
                    "description": "Additional metadata about the source",
                    "properties": {}
                }
            },
            "required": ["raw_content", "source_type"]
        },
        "returns": {
            "type": "object",
            "description": "Structured intake data with extracted information"
        }
    }


async def run(
    raw_content: str,
    source_type: str,
    metadata: Dict[str, Any] | None = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Parse raw client input into structured format.
    
    Args:
        raw_content: Raw client communication content
        source_type: Type of communication source
        metadata: Additional metadata about the source
        **kwargs: Additional parameters
        
    Returns:
        Dictionary containing structured intake data
        
    Raises:
        ValueError: If required parameters are missing or invalid
        RuntimeError: If parsing fails
    """
    # Validate input parameters
    if not raw_content or not raw_content.strip():
        raise ValueError("Raw content cannot be empty")
    
    if source_type not in ["email", "form", "direct_message", "phone_transcript", "document"]:
        raise ValueError(f"Invalid source type: {source_type}")
    
    # TODO: Implement actual parsing logic using LLM
    # This is a placeholder implementation
    
    # Mock parsing results based on content analysis
    parsed_data = {
        "client_name": "Extracted Client Name",
        "contact_email": "extracted@email.com",
        "project_title": "Extracted Project Title", 
        "functional_requirements": [
            "User authentication and authorization",
            "Data management and CRUD operations",
            "Reporting and analytics dashboard"
        ],
        "technical_requirements": [
            "Web-based application",
            "Database integration",
            "Responsive design"
        ],
        "budget_range": "To be determined",
        "timeline": "To be determined",
        "integration_needs": [],
        "compliance_requirements": []
    }
    
    # Create structured response
    result = {
        "status": ProcessingStatus.COMPLETED.value,
        "source_info": {
            "type": source_type,
            "content_length": len(raw_content),
            "metadata": metadata or {}
        },
        "extracted_data": parsed_data,
        "confidence_score": 0.8,  # Mock confidence
        "processing_notes": [
            "Placeholder implementation - requires LLM integration",
            f"Processed {len(raw_content)} characters of {source_type} content"
        ]
    }
    
    return result


def validate_parameters(parameters: Dict[str, Any]) -> ValidationResult:
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
    if "raw_content" not in parameters:
        errors.append("Missing required parameter: raw_content")
    elif not parameters["raw_content"].strip():
        errors.append("Raw content cannot be empty")
    
    if "source_type" not in parameters:
        errors.append("Missing required parameter: source_type")
    elif parameters["source_type"] not in ["email", "form", "direct_message", "phone_transcript", "document"]:
        errors.append(f"Invalid source_type: {parameters['source_type']}")
    
    # Check content length
    if "raw_content" in parameters and len(parameters["raw_content"]) > 100000:
        warnings.append("Content length exceeds recommended limit (100KB)")
    
    is_valid = len(errors) == 0
    score = 1.0 if is_valid else 0.0
    
    return ValidationResult(
        is_valid=is_valid,
        errors=errors,
        warnings=warnings,
        score=score
    )
