 """
Deterministic requirements extraction tool for analyzing structured intake data.

This tool processes parsed intake information to extract detailed
functional and technical requirements using rule-based analysis.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Requirement templates by category
FUNCTIONAL_REQUIREMENTS = {
    "authentication": [
        {
            "title": "User Registration",
            "description": "System shall allow users to create accounts with email verification",
            "priority": "high",
            "complexity": 3,
        },
        {
            "title": "User Login", 
            "description": "System shall provide secure login with password authentication",
            "priority": "high",
            "complexity": 2,
        },
        {
            "title": "Password Recovery",
            "description": "System shall allow users to reset forgotten passwords",
            "priority": "medium",
            "complexity": 2,
        },
    ],
    "data_management": [
        {
            "title": "Data Creation",
            "description": "System shall allow authorized users to create new records",
            "priority": "high",
            "complexity": 2,
        },
        {
            "title": "Data Retrieval",
            "description": "System shall provide efficient data search and retrieval",
            "priority": "high", 
            "complexity": 3,
        },
        {
            "title": "Data Updates",
            "description": "System shall allow authorized modification of existing records",
            "priority": "high",
            "complexity": 2,
        },
    ],
    "ecommerce": [
        {
            "title": "Product Catalog",
            "description": "System shall display products with images, descriptions, and pricing",
            "priority": "high",
            "complexity": 4,
        },
        {
            "title": "Shopping Cart",
            "description": "System shall allow users to add/remove items from cart",
            "priority": "high",
            "complexity": 3,
        },
        {
            "title": "Payment Processing",
            "description": "System shall securely process online payments",
            "priority": "high",
            "complexity": 5,
        },
    ],
    "reporting": [
        {
            "title": "Data Analytics",
            "description": "System shall provide insights and analytics dashboards",
            "priority": "medium",
            "complexity": 4,
        },
        {
            "title": "Export Functionality",
            "description": "System shall allow data export in common formats",
            "priority": "medium",
            "complexity": 2,
        },
    ],
}

TECHNICAL_REQUIREMENTS = {
    "web": [
        {
            "title": "Responsive Design",
            "description": "Application shall work on desktop, tablet, and mobile devices",
            "priority": "high",
            "complexity": 3,
        },
        {
            "title": "Browser Compatibility",
            "description": "Application shall support modern web browsers",
            "priority": "high",
            "complexity": 2,
        },
    ],
    "database": [
        {
            "title": "Data Storage",
            "description": "System shall use relational database for data persistence",
            "priority": "high",
            "complexity": 3,
        },
        {
            "title": "Data Backup",
            "description": "System shall implement automated data backup procedures",
            "priority": "high",
            "complexity": 2,
        },
    ],
    "security": [
        {
            "title": "Data Encryption",
            "description": "Sensitive data shall be encrypted at rest and in transit",
            "priority": "high",
            "complexity": 4,
        },
        {
            "title": "Access Control",
            "description": "System shall implement role-based access control",
            "priority": "high",
            "complexity": 3,
        },
    ],
    "performance": [
        {
            "title": "Response Time",
            "description": "System shall respond to user actions within 2 seconds",
            "priority": "medium",
            "complexity": 3,
        },
        {
            "title": "Scalability",
            "description": "System shall handle increased user load gracefully",
            "priority": "medium",
            "complexity": 4,
        },
    ],
}


def get_tool_metadata() -> dict[str, Any]:
    """Get metadata for the requirements extraction tool."""
    return {
        "name": "extract_requirements",
        "description": "Extract detailed requirements from parsed intake data using rule-based analysis",
        "version": "1.0.0",
        "category": "analysis",
        "parameters": {
            "type": "object",
            "properties": {
                "parsed_intake": {
                    "type": "object",
                    "description": "Structured intake data from parsing step",
                },
                "focus_areas": {
                    "type": "array",
                    "description": "Specific requirement categories to focus on",
                    "items": {"type": "string"},
                    "default": [],
                },
                "detail_level": {
                    "type": "string",
                    "enum": ["basic", "detailed", "comprehensive"],
                    "description": "Level of detail for requirement extraction",
                    "default": "detailed",
                },
            },
            "required": ["parsed_intake"],
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "functional_requirements": {
                    "type": "array",
                    "description": "List of functional requirements",
                },
                "technical_requirements": {
                    "type": "array", 
                    "description": "List of technical requirements",
                },
                "business_requirements": {
                    "type": "array",
                    "description": "List of business requirements",
                },
                "total_complexity": {
                    "type": "number",
                    "description": "Overall project complexity score",
                },
            },
        },
        "dependencies": [],
    }


def run(parameters: dict[str, Any]) -> dict[str, Any]:
    """
    Extract detailed requirements from parsed intake data.
    
    Args:
        parameters: Tool execution parameters
        
    Returns:
        Dictionary containing detailed requirements analysis
    """
    parsed_intake = parameters.get("parsed_intake", {})
    focus_areas = parameters.get("focus_areas", [])
    detail_level = parameters.get("detail_level", "detailed")
    
    if not parsed_intake:
        return {
            "error": "No parsed intake data provided",
            "functional_requirements": [],
            "technical_requirements": [],
            "business_requirements": [],
            "total_complexity": 0,
        }
    
    logger.info("Extracting requirements with %s detail level", detail_level)
    
    # Extract project type and business context
    business_type = parsed_intake.get("business_type", "general")
    requirements = parsed_intake.get("requirements", [])
    
    # Generate functional requirements
    functional_reqs = _extract_functional_requirements(requirements, business_type, focus_areas)
    
    # Generate technical requirements
    technical_reqs = _extract_technical_requirements(requirements, business_type, focus_areas)
    
    # Generate business requirements
    business_reqs = _extract_business_requirements(parsed_intake, business_type)
    
    # Adjust detail level
    if detail_level == "basic":
        functional_reqs = functional_reqs[:3]
        technical_reqs = technical_reqs[:3]
        business_reqs = business_reqs[:2]
    elif detail_level == "comprehensive":
        functional_reqs.extend(_get_additional_requirements(business_type))
    
    # Calculate complexity
    total_complexity = _calculate_complexity(functional_reqs, technical_reqs, business_reqs)
    
    return {
        "functional_requirements": functional_reqs,
        "technical_requirements": technical_reqs,
        "business_requirements": business_reqs,
        "total_complexity": total_complexity,
        "analysis_metadata": {
            "business_type": business_type,
            "detail_level": detail_level,
            "focus_areas": focus_areas,
            "requirement_counts": {
                "functional": len(functional_reqs),
                "technical": len(technical_reqs),
                "business": len(business_reqs),
            },
        },
    }


def _extract_functional_requirements(
    requirements: list[dict[str, Any]], 
    business_type: str, 
    focus_areas: list[str],
) -> list[dict[str, Any]]:
    """Extract functional requirements based on project needs."""
    extracted = []
    
    # Always include basic authentication if it's a web project
    req_types = [req.get("type", "") for req in requirements]
    if any(t in ["website", "web_app", "mobile_app"] for t in req_types):
        extracted.extend(_get_requirements_by_category("authentication"))
    
    # Add data management if mentioned
    if any("data" in req.get("type", "") for req in requirements):
        extracted.extend(_get_requirements_by_category("data_management"))
    
    # Add ecommerce requirements if business type indicates
    if business_type == "ecommerce" or any("ecommerce" in req.get("type", "") for req in requirements):
        extracted.extend(_get_requirements_by_category("ecommerce"))
    
    # Add reporting if mentioned or premium tier
    if any("report" in str(req).lower() for req in requirements) or business_type in ["saas", "analytics"]:
        extracted.extend(_get_requirements_by_category("reporting"))
    
    # Filter by focus areas if specified
    if focus_areas:
        extracted = [req for req in extracted if req.get("category") in focus_areas]
    
    return _add_requirement_ids(extracted, "FR")


def _extract_technical_requirements(
    requirements: list[dict[str, Any]], 
    business_type: str, 
    focus_areas: list[str],
) -> list[dict[str, Any]]:
    """Extract technical requirements based on project needs."""
    extracted = []
    
    # Web requirements for web projects
    req_types = [req.get("type", "") for req in requirements]
    if any(t in ["website", "web_app"] for t in req_types):
        extracted.extend(_get_tech_requirements_by_category("web"))
    
    # Database requirements for data-driven projects
    if any(t in ["backend", "database"] for t in req_types) or business_type == "saas":
        extracted.extend(_get_tech_requirements_by_category("database"))
    
    # Security requirements for sensitive industries
    if business_type in ["healthcare", "fintech", "legal"] or "security" in focus_areas:
        extracted.extend(_get_tech_requirements_by_category("security"))
    
    # Performance requirements for high-traffic projects
    if business_type in ["ecommerce", "saas"] or "performance" in focus_areas:
        extracted.extend(_get_tech_requirements_by_category("performance"))
    
    # Filter by focus areas if specified
    if focus_areas:
        extracted = [req for req in extracted if req.get("category") in focus_areas]
    
    return _add_requirement_ids(extracted, "TR")


def _extract_business_requirements(parsed_intake: dict[str, Any], business_type: str) -> list[dict[str, Any]]:
    """Extract business requirements from intake data."""
    business_reqs = []
    
    # Timeline requirements
    timeline = parsed_intake.get("timeline", {})
    if timeline:
        business_reqs.append({
            "title": "Project Timeline",
            "description": "Project shall be completed according to specified timeline constraints",
            "priority": "high",
            "category": "timeline",
            "complexity": 1,
        })
    
    # Budget requirements
    budget = parsed_intake.get("budget", {})
    if budget and budget.get("type") != "not_specified":
        business_reqs.append({
            "title": "Budget Constraints",
            "description": "Project shall be delivered within approved budget limits",
            "priority": "high", 
            "category": "budget",
            "complexity": 1,
        })
    
    # User experience requirements
    business_reqs.append({
        "title": "User Experience",
        "description": "System shall provide intuitive and user-friendly interface",
        "priority": "medium",
        "category": "usability",
        "complexity": 2,
    })
    
    # Industry-specific business requirements
    if business_type == "healthcare":
        business_reqs.append({
            "title": "HIPAA Compliance",
            "description": "System shall comply with healthcare privacy regulations",
            "priority": "high",
            "category": "compliance",
            "complexity": 4,
        })
    elif business_type == "fintech":
        business_reqs.append({
            "title": "Financial Compliance",
            "description": "System shall meet financial industry regulatory requirements",
            "priority": "high",
            "category": "compliance",
            "complexity": 4,
        })
    
    return _add_requirement_ids(business_reqs, "BR")


def _get_requirements_by_category(category: str) -> list[dict[str, Any]]:
    """Get functional requirements by category."""
    reqs = FUNCTIONAL_REQUIREMENTS.get(category, [])
    return [dict(req, category=category) for req in reqs]


def _get_tech_requirements_by_category(category: str) -> list[dict[str, Any]]:
    """Get technical requirements by category."""
    reqs = TECHNICAL_REQUIREMENTS.get(category, [])
    return [dict(req, category=category) for req in reqs]


def _get_additional_requirements(business_type: str) -> list[dict[str, Any]]:
    """Get additional requirements for comprehensive detail level."""
    additional = []
    
    if business_type == "healthcare":
        additional.extend([
            {
                "title": "Audit Trail",
                "description": "System shall maintain comprehensive audit logs",
                "priority": "high",
                "category": "compliance",
                "complexity": 3,
            },
        ])
    elif business_type == "ecommerce":
        additional.extend([
            {
                "title": "Inventory Management",
                "description": "System shall track product inventory levels",
                "priority": "medium",
                "category": "inventory",
                "complexity": 4,
            },
        ])
    
    return _add_requirement_ids(additional, "AR")


def _add_requirement_ids(requirements: list[dict[str, Any]], prefix: str) -> list[dict[str, Any]]:
    """Add unique IDs to requirements."""
    for i, req in enumerate(requirements, 1):
        req["id"] = f"{prefix}-{i:03d}"
    return requirements


def _calculate_complexity(
    functional: list[dict[str, Any]], 
    technical: list[dict[str, Any]], 
    business: list[dict[str, Any]],
) -> float:
    """Calculate total project complexity score."""
    all_reqs = functional + technical + business
    if not all_reqs:
        return 0.0
    
    total_complexity = sum(req.get("complexity", 1) for req in all_reqs)
    return round(total_complexity / len(all_reqs), 2)
