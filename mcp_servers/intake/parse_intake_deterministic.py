"""
Deterministic intake parsing tool.

This tool uses regex and string utilities to parse raw intake content 
into normalized JSON structures without LLM dependencies.
"""

import json
import logging
import re
from datetime import datetime
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def get_tool_metadata() -> Dict[str, Any]:
    """
    Get metadata for the intake parsing tool.
    
    Returns:
        Dictionary containing tool metadata including parameters,
        description, and expected output format.
    """
    return {
        "name": "parse_intake",
        "description": "Deterministically parse raw client intake content using regex and string utilities",
        "version": "1.0.0",
        "category": "intake",
        "parameters": {
            "type": "object",
            "properties": {
                "input_data": {
                    "type": "string", 
                    "description": "Raw intake content to parse",
                    "required": True
                },
                "source_type": {
                    "type": "string",
                    "enum": ["form_submission", "email_thread", "direct_message", "auto_detect"],
                    "description": "Type of input source",
                    "default": "auto_detect"
                },
                "client_tier": {
                    "type": "string", 
                    "enum": ["starter", "business", "premium"],
                    "description": "Client tier for processing context",
                    "default": "business"
                }
            },
            "required": ["input_data"]
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "intake_data": {
                    "type": "object",
                    "description": "Parsed and structured intake information"
                },
                "confidence_score": {
                    "type": "number",
                    "description": "Confidence in parsing accuracy (0-1)"
                },
                "data_quality": {
                    "type": "string",
                    "enum": ["high", "medium", "low"]
                }
            }
        },
        "dependencies": ["mcp_servers.skills.cleaning", "mcp_servers.skills.validators"]
    }


def run(parameters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute deterministic intake parsing using regex and string utilities.
    
    Args:
        parameters: Tool execution parameters containing input_data and options
        
    Returns:
        Dictionary with parsed intake data and quality metrics
    """
    # Validate required parameters
    if "input_data" not in parameters:
        raise ValueError("Missing required parameter: input_data")
    
    input_data = parameters["input_data"]
    source_type = parameters.get("source_type", "auto_detect")
    client_tier = parameters.get("client_tier", "business")
    
    logger.info("Processing intake data: source_type=%s, tier=%s", source_type, client_tier)
    
    # Normalize input text
    normalized_content = _normalize_text(input_data)
    
    # Extract contact information  
    contact_info = _extract_contact_info(normalized_content)
    
    # Detect source type if auto-detect
    if source_type == "auto_detect":
        source_type = _detect_source_type(normalized_content)
    
    # Parse based on source type
    if source_type == "form_submission":
        parsed_data = _parse_form_submission(normalized_content, contact_info)
    elif source_type == "email_thread":
        parsed_data = _parse_email_thread(normalized_content, contact_info)
    elif source_type == "direct_message":
        parsed_data = _parse_direct_message(normalized_content, contact_info)
    else:
        parsed_data = _parse_generic_content(normalized_content, contact_info)
    
    # Add metadata
    parsed_data["source_metadata"] = {
        "detected_type": source_type,
        "original_length": len(input_data),
        "normalized_length": len(normalized_content),
        "processing_timestamp": datetime.utcnow().isoformat(),
        "client_tier": client_tier
    }
    
    # Calculate quality metrics
    confidence_score = _calculate_confidence(parsed_data, normalized_content)
    data_quality = _assess_data_quality(parsed_data, confidence_score)
    
    # Validate extracted data
    validation_results = _validate_parsed_data(parsed_data)
    
    return {
        "intake_data": parsed_data,
        "confidence_score": confidence_score,
        "data_quality": data_quality,
        "validation_results": validation_results,
        "processing_metadata": {
            "tool": "parse_intake",
            "version": "1.0.0",
            "timestamp": datetime.utcnow().isoformat(),
            "client_tier": client_tier,
            "source_type": source_type
        }
    }


def _normalize_text(content: str) -> str:
    """Normalize text by removing extra whitespace and standardizing format."""
    # Remove excessive whitespace
    normalized = re.sub(r'\s+', ' ', content)
    # Remove leading/trailing whitespace
    normalized = normalized.strip()
    return normalized


def _extract_contact_info(content: str) -> Dict[str, str]:
    """Extract contact information using regex patterns."""
    contact_info = {}
    
    # Email extraction
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    emails = re.findall(email_pattern, content)
    if emails:
        contact_info["email"] = emails[0]
    
    # Phone extraction
    phone_pattern = r'(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})'
    phones = re.findall(phone_pattern, content)
    if phones:
        contact_info["phone"] = f"({phones[0][0]}) {phones[0][1]}-{phones[0][2]}"
    
    # Name extraction (simple patterns)
    name_patterns = [
        r'(?:name|client)[:\s]*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        r'^([A-Z][a-z]+\s+[A-Z][a-z]+)',  # FirstName LastName at start
    ]
    
    for pattern in name_patterns:
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            contact_info["name"] = match.group(1).strip()
            break
    
    return contact_info


def _detect_source_type(content: str) -> str:
    """Auto-detect the source type using deterministic patterns."""
    content_lower = content.lower()
    
    # Email thread indicators (highest priority)
    email_indicators = ["from:", "to:", "subject:", "re:", "sent:", "date:", "cc:"]
    email_score = sum(1 for indicator in email_indicators if indicator in content_lower)
    
    # Form submission indicators
    form_indicators = ["name:", "email:", "company:", "phone:", "message:", "form"]
    form_score = sum(1 for indicator in form_indicators if indicator in content_lower)
    
    # Direct message indicators  
    dm_indicators = ["hey", "hi", "hello", "chat", "dm", "message", "whatsapp", "slack"]
    dm_score = sum(1 for indicator in dm_indicators if indicator in content_lower)
    
    if email_score >= 2:
        return "email_thread"
    elif form_score >= 3:
        return "form_submission"
    elif dm_score >= 2:
        return "direct_message"
    elif form_score >= dm_score:
        return "form_submission"
    else:
        return "direct_message"


def _parse_form_submission(content: str, contact_info: Dict[str, str]) -> Dict[str, Any]:
    """Parse structured form submission content."""
    parsed = {
        "client_name": contact_info.get("name", _extract_form_field(content, "name")),
        "contact_email": contact_info.get("email", _extract_form_field(content, "email")),
        "phone": contact_info.get("phone", _extract_form_field(content, "phone")),
        "company": _extract_form_field(content, "company"),
        "business_type": _extract_business_type(content),
        "project_title": _extract_form_field(content, "project"),
        "requirements": _extract_requirements_structured(content),
        "timeline": _extract_timeline_info(content),
        "budget": _extract_budget_info(content),
        "additional_notes": _extract_form_field(content, "notes"),
    }
    
    return {k: v for k, v in parsed.items() if v}  # Remove empty values


def _parse_email_thread(content: str, contact_info: Dict[str, str]) -> Dict[str, Any]:
    """Parse email thread content with conversation flow."""
    # Extract email headers
    headers = _extract_email_headers(content)
    
    # Split into individual messages
    messages = _split_email_messages(content)
    
    parsed = {
        "participants": list(set([headers.get("from_email", ""), headers.get("to", "")])),
        "subject": headers.get("subject", ""),
        "message_count": len(messages),
        "client_name": contact_info.get("name", headers.get("from_name", "")),
        "contact_email": contact_info.get("email", headers.get("from_email", "")),
        "business_type": _extract_business_type(content),
        "requirements": _extract_requirements_conversational(content),
        "timeline": _extract_timeline_info(content),
        "budget": _extract_budget_info(content),
        "conversation_flow": [{"message_id": i, "length": len(msg)} for i, msg in enumerate(messages)],
    }
    
    return {k: v for k, v in parsed.items() if v}


def _parse_direct_message(content: str, contact_info: Dict[str, str]) -> Dict[str, Any]:
    """Parse direct message content with noise filtering."""
    # Filter out conversational noise
    business_content = _filter_dm_noise(content)
    
    parsed = {
        "client_name": contact_info.get("name", _extract_dm_name(content)),
        "contact_email": contact_info.get("email", ""),
        "phone": contact_info.get("phone", ""),
        "business_type": _extract_business_type(content),
        "requirements": _extract_requirements_conversational(business_content),
        "timeline": _extract_timeline_info(content),
        "budget": _extract_budget_info(content),
        "noise_level": _assess_noise_level(content, business_content),
        "business_content_ratio": len(business_content) / len(content) if content else 0,
        "key_phrases": _extract_business_phrases(business_content),
    }
    
    return {k: v for k, v in parsed.items() if v}


def _parse_generic_content(content: str, contact_info: Dict[str, str]) -> Dict[str, Any]:
    """Parse content with unknown structure."""
    parsed = {
        "client_name": contact_info.get("name", ""),
        "contact_email": contact_info.get("email", ""),
        "phone": contact_info.get("phone", ""),
        "business_type": _extract_business_type(content),
        "requirements": _extract_requirements_generic(content),
        "timeline": _extract_timeline_info(content),
        "budget": _extract_budget_info(content),
    }
    
    return {k: v for k, v in parsed.items() if v}


def _extract_form_field(content: str, field_name: str) -> str:
    """Extract specific field from form-like content."""
    patterns = {
        "name": [r"(?:name|client)[:\s]*([A-Za-z\s]{2,50})", r"^([A-Z][a-z]+\s+[A-Z][a-z]+)"],
        "email": [r"(?:email|e-mail)[:\s]*([A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,})"],
        "phone": [r"(?:phone|tel)[:\s]*([0-9\-\(\)\s]{10,})"],
        "company": [r"(?:company|organization)[:\s]*([A-Za-z0-9\s&.,]{2,50})"],
        "project": [r"(?:project|title)[:\s]*([A-Za-z0-9\s]{5,100})"],
        "notes": [r"(?:notes|comments|message)[:\s]*([A-Za-z0-9\s.,!?]{10,500})"],
    }
    
    for pattern in patterns.get(field_name, []):
        match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
        if match:
            return match.group(1).strip()
    
    return ""


def _extract_email_headers(content: str) -> Dict[str, str]:
    """Extract email headers from email thread content."""
    headers = {}
    
    # Common email header patterns
    header_patterns = {
        "from": r"from[:\s]+(.+?)(?:\n|$)",
        "to": r"to[:\s]+(.+?)(?:\n|$)", 
        "subject": r"subject[:\s]+(.+?)(?:\n|$)",
        "date": r"(?:date|sent)[:\s]+(.+?)(?:\n|$)",
    }
    
    for header, pattern in header_patterns.items():
        match = re.search(pattern, content, re.IGNORECASE | re.MULTILINE)
        if match:
            headers[header] = match.group(1).strip()
    
    # Extract name and email from 'from' field
    if "from" in headers:
        from_match = re.search(r"(.+?)\s*<(.+?)>", headers["from"])
        if from_match:
            headers["from_name"] = from_match.group(1).strip()
            headers["from_email"] = from_match.group(2).strip()
        else:
            headers["from_email"] = headers["from"]
    
    return headers


def _split_email_messages(content: str) -> List[str]:
    """Split email thread into individual messages."""
    # Look for common email separation patterns
    separators = [
        r"^From[:\s]",
        r"^On\s+.+wrote:",
        r"^-{5,}",
        r"^>{3,}",
    ]
    
    messages = [content]  # Start with full content
    
    for separator in separators:
        new_messages = []
        for message in messages:
            parts = re.split(separator, message, flags=re.MULTILINE)
            new_messages.extend([part.strip() for part in parts if part.strip()])
        messages = new_messages
    
    return messages[:10]  # Limit to reasonable number


def _extract_requirements_structured(content: str) -> List[Dict[str, Any]]:
    """Extract requirements from structured content."""
    requirements = []
    
    # Technical requirement patterns
    tech_patterns = {
        "website": [r"website", r"web\s*site", r"web\s*app"],
        "mobile_app": [r"mobile", r"app", r"ios", r"android"],
        "backend": [r"backend", r"server", r"api", r"database"],
        "integration": [r"integration", r"integrate", r"third.party"],
        "ecommerce": [r"e.commerce", r"shop", r"store", r"payment"],
        "cms": [r"cms", r"content.management"],
    }
    
    content_lower = content.lower()
    for req_type, patterns in tech_patterns.items():
        matches = []
        for pattern in patterns:
            matches.extend(re.findall(pattern, content_lower))
        
        if matches:
            requirements.append({
                "type": req_type,
                "confidence": min(0.9, len(matches) * 0.3),
                "evidence": matches[:3],  # First 3 matches
                "source": "structured_content"
            })
    
    return requirements


def _extract_requirements_conversational(content: str) -> List[Dict[str, Any]]:
    """Extract requirements from conversational content."""
    requirements = []
    
    # Conversational requirement patterns
    conversation_patterns = {
        "website": [r"need.+website", r"want.+website", r"build.+website"],
        "app": [r"need.+app", r"want.+app", r"mobile.+app"],
        "redesign": [r"redesign", r"update.+site", r"modernize"],
        "integration": [r"connect.+system", r"integrate.+with"],
    }
    
    content_lower = content.lower()
    for req_type, patterns in conversation_patterns.items():
        for pattern in patterns:
            if re.search(pattern, content_lower):
                requirements.append({
                    "type": req_type,
                    "confidence": 0.7,
                    "evidence": [pattern],
                    "source": "conversational_content"
                })
                break  # Only add once per type
    
    return requirements


def _extract_requirements_generic(content: str) -> List[Dict[str, Any]]:
    """Extract requirements from generic content."""
    return _extract_requirements_structured(content)


def _extract_business_type(content: str) -> str:
    """Extract business type using keyword matching."""
    content_lower = content.lower()
    
    business_patterns = {
        "healthcare": [r"medical", r"health", r"clinic", r"hospital", r"hipaa", r"doctor"],
        "ecommerce": [r"e.commerce", r"shop", r"store", r"retail", r"product"],
        "fintech": [r"financial", r"bank", r"payment", r"crypto", r"trading"],
        "saas": [r"saas", r"software", r"platform", r"subscription"],
        "education": [r"education", r"school", r"university", r"course", r"learning"],
        "consulting": [r"consulting", r"advisory", r"strategy"],
        "manufacturing": [r"manufacturing", r"factory", r"production"],
        "nonprofit": [r"nonprofit", r"charity", r"foundation", r"ngo"],
    }
    
    for business_type, patterns in business_patterns.items():
        if any(re.search(pattern, content_lower) for pattern in patterns):
            return business_type
    
    return "general"


def _extract_timeline_info(content: str) -> Dict[str, Any]:
    """Extract timeline information from content."""
    timeline = {"constraints": [], "urgency": "normal"}
    
    # Timeline patterns
    timeline_patterns = [
        (r"(\d+)\s*(week|month)s?", "duration"),
        (r"by\s+([A-Za-z]+\s+\d{1,2})", "deadline"),
        (r"(urgent|asap|rush)", "priority"),
        (r"(\d{1,2}/\d{1,2}/\d{2,4})", "date"),
    ]
    
    for pattern, constraint_type in timeline_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        for match in matches:
            timeline["constraints"].append({
                "type": constraint_type,
                "value": match if isinstance(match, str) else " ".join(match),
            })
    
    # Check urgency
    if re.search(r"urgent|asap|rush|immediately", content, re.IGNORECASE):
        timeline["urgency"] = "high"
    
    return timeline if timeline["constraints"] else {}


def _extract_budget_info(content: str) -> Dict[str, Any]:
    """Extract budget information from content."""
    # Look for budget patterns
    budget_patterns = [
        r"\$([0-9,]+)",  # Dollar amounts
        r"budget[:\s]+\$?([0-9,]+)",
        r"([0-9]+)k\s*budget",  # 50k budget
    ]
    
    amounts = []
    for pattern in budget_patterns:
        matches = re.findall(pattern, content, re.IGNORECASE)
        amounts.extend(matches)
    
    if amounts:
        # Convert to numeric (simple parsing)
        try:
            amount_str = amounts[0].replace(",", "")
            if "k" in content.lower():
                amount = int(amount_str) * 1000
            else:
                amount = int(amount_str)
            
            return {
                "amount": amount,
                "currency": "USD",
                "type": "estimated",
                "confidence": 0.7
            }
        except ValueError:
            pass
    
    return {"type": "not_specified", "confidence": 0.0}


def _filter_dm_noise(content: str) -> str:
    """Filter out conversational noise from direct messages."""
    lines = content.split('\n')
    business_lines = []
    
    # Noise patterns to filter out
    noise_patterns = [
        r"^(hey|hi|hello|yo)\s*$",
        r"^(ok|okay|cool|sure|thanks|thx)\s*$",
        r"^lol\s*$",
        r"^(brb|gtg|ttyl)\s*$",
        r"^\s*$",  # Empty lines
    ]
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        is_noise = any(re.match(pattern, line, re.IGNORECASE) for pattern in noise_patterns)
        if not is_noise:
            business_lines.append(line)
    
    return '\n'.join(business_lines)


def _extract_dm_name(content: str) -> str:
    """Extract name from direct message content."""
    # Look for self-introduction patterns
    intro_patterns = [
        r"i'm\s+([A-Z][a-z]+)",
        r"my\s+name\s+is\s+([A-Z][a-z]+)",
        r"this\s+is\s+([A-Z][a-z]+)",
    ]
    
    for pattern in intro_patterns:
        match = re.search(pattern, content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return ""


def _assess_noise_level(original_content: str, filtered_content: str) -> str:
    """Assess the noise level in the content."""
    if not original_content:
        return "unknown"
    
    noise_ratio = 1 - (len(filtered_content) / len(original_content))
    
    if noise_ratio > 0.7:
        return "high"
    elif noise_ratio > 0.4:
        return "medium"
    else:
        return "low"


def _extract_business_phrases(content: str) -> List[str]:
    """Extract key business-related phrases."""
    business_keywords = [
        "website", "app", "system", "platform", "integration", "database",
        "crm", "ecommerce", "payment", "analytics", "security", "mobile"
    ]
    
    phrases = []
    content_lower = content.lower()
    
    for keyword in business_keywords:
        if keyword in content_lower:
            phrases.append(keyword)
    
    return phrases


def _calculate_confidence(parsed_data: Dict[str, Any], content: str) -> float:
    """Calculate parsing confidence based on extracted data completeness."""
    score = 0.0
    max_score = 8.0
    
    # Core identification fields (high weight)
    if parsed_data.get("client_name") and len(parsed_data["client_name"]) > 2:
        score += 2.0
    if parsed_data.get("contact_email") and "@" in parsed_data["contact_email"]:
        score += 2.0
    
    # Business context fields (medium weight)
    if parsed_data.get("business_type") and parsed_data["business_type"] != "general":
        score += 1.0
    if parsed_data.get("requirements") and len(parsed_data["requirements"]) > 0:
        score += 1.0
    
    # Additional detail fields (lower weight)
    if parsed_data.get("timeline"):
        score += 1.0
    if parsed_data.get("budget") and parsed_data["budget"].get("type") != "not_specified":
        score += 1.0
    
    return min(1.0, score / max_score)


def _assess_data_quality(parsed_data: Dict[str, Any], confidence_score: float) -> str:
    """Assess overall data quality."""
    # Count non-empty key fields
    key_fields = ["client_name", "contact_email", "business_type", "requirements"]
    populated_fields = sum(1 for field in key_fields if parsed_data.get(field))
    
    if confidence_score >= 0.8 and populated_fields >= 3:
        return "high"
    elif confidence_score >= 0.5 and populated_fields >= 2:
        return "medium"
    else:
        return "low"


def _validate_parsed_data(parsed_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate extracted data using validation utilities."""
    validation_results = {
        "valid_fields": [],
        "invalid_fields": [],
        "warnings": []
    }
    
    # Validate email
    if parsed_data.get("contact_email"):
        if _validate_email(parsed_data["contact_email"]):
            validation_results["valid_fields"].append("contact_email")
        else:
            validation_results["invalid_fields"].append("contact_email")
    
    # Validate phone
    if parsed_data.get("phone"):
        if _validate_phone(parsed_data["phone"]):
            validation_results["valid_fields"].append("phone")
        else:
            validation_results["invalid_fields"].append("phone")
    
    # Check for completeness
    if not parsed_data.get("client_name"):
        validation_results["warnings"].append("Missing client name")
    if not parsed_data.get("requirements"):
        validation_results["warnings"].append("No requirements extracted")
    
    return validation_results


def _validate_email(email: str) -> bool:
    """Simple email validation."""
    pattern = r'^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}$'
    return bool(re.match(pattern, email))


def _validate_phone(phone: str) -> bool:
    """Simple phone validation."""
    # Remove all non-digits
    digits = re.sub(r'\D', '', phone)
    # Check if it's 10 or 11 digits (with country code)
    return len(digits) in [10, 11]
