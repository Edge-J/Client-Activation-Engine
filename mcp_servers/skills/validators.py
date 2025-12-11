"""
Shared validation utilities for MCP tools.

This module provides deterministic validation functions that can be used
across different MCP tools for data integrity and quality assurance.
"""

import re
import logging
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from urllib.parse import urlparse

logger = logging.getLogger(__name__)


def validate_email(email: str) -> bool:
    """
    Validate email address format using RFC-compliant regex.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email is valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    # RFC 5322 compliant email regex (simplified)
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def validate_phone(phone: str) -> bool:
    """
    Validate phone number format (US/International).
    
    Args:
        phone: Phone number to validate
        
    Returns:
        True if phone is valid, False otherwise
    """
    if not phone or not isinstance(phone, str):
        return False
    
    # Remove all non-digits
    digits = re.sub(r'\D', '', phone.strip())
    
    # Check if it's 10 or 11 digits (with country code)
    return len(digits) in [10, 11]


def validate_url(url: str) -> bool:
    """
    Validate URL format and structure.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is valid, False otherwise
    """
    if not url or not isinstance(url, str):
        return False
    
    try:
        result = urlparse(url.strip())
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def validate_business_type(business_type: str) -> bool:
    """
    Validate business type against known categories.
    
    Args:
        business_type: Business type to validate
        
    Returns:
        True if business type is recognized, False otherwise
    """
    if not business_type or not isinstance(business_type, str):
        return False
    
    valid_types = {
        "healthcare", "ecommerce", "fintech", "saas", "education", 
        "consulting", "manufacturing", "nonprofit", "real_estate", 
        "legal", "media", "hospitality", "technology", "retail", 
        "finance", "general"
    }
    
    return business_type.lower().strip() in valid_types


def validate_timeline_constraint(constraint: Dict[str, Any]) -> bool:
    """
    Validate timeline constraint structure and values.
    
    Args:
        constraint: Timeline constraint dictionary
        
    Returns:
        True if constraint is valid, False otherwise
    """
    if not isinstance(constraint, dict):
        return False
    
    required_fields = ["type", "value"]
    if not all(field in constraint for field in required_fields):
        return False
    
    valid_types = ["duration", "deadline", "priority", "date"]
    return constraint["type"] in valid_types and constraint["value"]


def validate_budget_info(budget: Dict[str, Any]) -> bool:
    """
    Validate budget information structure and values.
    
    Args:
        budget: Budget information dictionary
        
    Returns:
        True if budget is valid, False otherwise
    """
    if not isinstance(budget, dict):
        return False
    
    # Must have type field
    if "type" not in budget:
        return False
    
    valid_types = ["estimated", "fixed", "range", "not_specified"]
    if budget["type"] not in valid_types:
        return False
    
    # If amount is specified, validate it
    if "amount" in budget:
        try:
            amount = float(budget["amount"])
            return amount >= 0
        except (ValueError, TypeError):
            return False
    
    return True


def validate_requirement(requirement: Dict[str, Any]) -> bool:
    """
    Validate requirement structure and completeness.
    
    Args:
        requirement: Requirement dictionary
        
    Returns:
        True if requirement is valid, False otherwise
    """
    if not isinstance(requirement, dict):
        return False
    
    required_fields = ["type", "confidence"]
    if not all(field in requirement for field in required_fields):
        return False
    
    # Validate confidence score
    try:
        confidence = float(requirement["confidence"])
        if not 0.0 <= confidence <= 1.0:
            return False
    except (ValueError, TypeError):
        return False
    
    # Validate type is not empty
    return bool(requirement["type"] and isinstance(requirement["type"], str))


def validate_contact_info(contact: Dict[str, str]) -> Tuple[bool, List[str]]:
    """
    Validate contact information completeness and format.
    
    Args:
        contact: Contact information dictionary
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    if not isinstance(contact, dict):
        return False, ["Contact info must be a dictionary"]
    
    # Validate email if present
    if "email" in contact:
        if not validate_email(contact["email"]):
            errors.append("Invalid email format")
    
    # Validate phone if present
    if "phone" in contact:
        if not validate_phone(contact["phone"]):
            errors.append("Invalid phone format")
    
    # Check for minimum contact info
    has_email = "email" in contact and contact["email"]
    has_phone = "phone" in contact and contact["phone"]
    
    if not (has_email or has_phone):
        errors.append("Must have at least email or phone")
    
    return len(errors) == 0, errors


def validate_asset_info(asset: Dict[str, Any]) -> bool:
    """
    Validate asset information structure.
    
    Args:
        asset: Asset information dictionary
        
    Returns:
        True if asset is valid, False otherwise
    """
    if not isinstance(asset, dict):
        return False
    
    required_fields = ["type", "name"]
    if not all(field in asset for field in required_fields):
        return False
    
    valid_types = ["logo", "image", "document", "video", "audio", "other"]
    return asset["type"] in valid_types and bool(asset["name"])


def validate_confidence_score(score: Any) -> bool:
    """
    Validate confidence score is a valid number between 0 and 1.
    
    Args:
        score: Confidence score to validate
        
    Returns:
        True if score is valid, False otherwise
    """
    try:
        score_float = float(score)
        return 0.0 <= score_float <= 1.0
    except (ValueError, TypeError):
        return False


def validate_data_quality(quality: str) -> bool:
    """
    Validate data quality assessment value.
    
    Args:
        quality: Quality assessment string
        
    Returns:
        True if quality is valid, False otherwise
    """
    if not isinstance(quality, str):
        return False
    
    valid_qualities = ["high", "medium", "low"]
    return quality.lower().strip() in valid_qualities


def validate_complexity_level(complexity: str) -> bool:
    """
    Validate complexity level assessment.
    
    Args:
        complexity: Complexity level string
        
    Returns:
        True if complexity is valid, False otherwise
    """
    if not isinstance(complexity, str):
        return False
    
    valid_levels = ["low", "medium", "high", "enterprise"]
    return complexity.lower().strip() in valid_levels


def validate_industry_classification(classification: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """
    Validate industry classification result structure.
    
    Args:
        classification: Industry classification dictionary
        
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []
    
    if not isinstance(classification, dict):
        return False, ["Classification must be a dictionary"]
    
    # Required fields
    required_fields = ["normalized_industry", "confidence_score"]
    for field in required_fields:
        if field not in classification:
            errors.append(f"Missing required field: {field}")
    
    # Validate confidence score
    if "confidence_score" in classification:
        if not validate_confidence_score(classification["confidence_score"]):
            errors.append("Invalid confidence score")
    
    # Validate industry
    if "normalized_industry" in classification:
        if not validate_business_type(classification["normalized_industry"]):
            errors.append("Invalid industry classification")
    
    return len(errors) == 0, errors


def validate_processing_metadata(metadata: Dict[str, Any]) -> bool:
    """
    Validate processing metadata structure.
    
    Args:
        metadata: Processing metadata dictionary
        
    Returns:
        True if metadata is valid, False otherwise
    """
    if not isinstance(metadata, dict):
        return False
    
    required_fields = ["tool", "version", "timestamp"]
    if not all(field in metadata for field in required_fields):
        return False
    
    # Validate timestamp format
    if "timestamp" in metadata:
        try:
            datetime.fromisoformat(metadata["timestamp"].replace('Z', '+00:00'))
        except (ValueError, AttributeError):
            return False
    
    return True


def sanitize_text_input(text: str, max_length: int = 10000) -> str:
    """
    Sanitize text input by removing potentially harmful content.
    
    Args:
        text: Input text to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized text
    """
    if not isinstance(text, str):
        return ""
    
    # Truncate if too long
    sanitized = text[:max_length]
    
    # Remove potential script tags and other harmful content
    sanitized = re.sub(r'<script[^>]*>.*?</script>', '', sanitized, flags=re.IGNORECASE | re.DOTALL)
    sanitized = re.sub(r'javascript:', '', sanitized, flags=re.IGNORECASE)
    
    # Normalize whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    return sanitized


def validate_file_path(file_path: str) -> bool:
    """
    Validate file path for security (basic path traversal prevention).
    
    Args:
        file_path: File path to validate
        
    Returns:
        True if path is safe, False otherwise
    """
    if not file_path or not isinstance(file_path, str):
        return False
    
    # Basic security checks
    dangerous_patterns = ['../', '..\\', '/etc/', '/proc/', 'C:\\Windows\\']
    
    for pattern in dangerous_patterns:
        if pattern in file_path:
            return False
    
    return True


def get_validation_summary(data: Dict[str, Any], validations: List[Tuple[str, bool]]) -> Dict[str, Any]:
    """
    Generate a validation summary for reporting.
    
    Args:
        data: Data that was validated
        validations: List of (field_name, is_valid) tuples
        
    Returns:
        Validation summary dictionary
    """
    total_checks = len(validations)
    passed_checks = sum(1 for _, is_valid in validations if is_valid)
    
    failed_fields = [field for field, is_valid in validations if not is_valid]
    
    return {
        "total_checks": total_checks,
        "passed_checks": passed_checks,
        "failed_checks": total_checks - passed_checks,
        "success_rate": passed_checks / total_checks if total_checks > 0 else 0.0,
        "failed_fields": failed_fields,
        "overall_valid": len(failed_fields) == 0,
        "validation_timestamp": datetime.utcnow().isoformat(),
    }
