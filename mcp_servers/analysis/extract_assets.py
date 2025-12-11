"""
Deterministic asset extraction tool for project scoping.

This tool analyzes requirements to identify and catalog project assets,
resources, and deliverables using rule-based classification.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Asset categories and templates
ASSET_TEMPLATES = {
    "frontend": {
        "web_pages": [
            "Homepage/Landing page",
            "About page", 
            "Contact page",
            "Services/Products page",
            "User dashboard",
            "Login/Registration pages",
        ],
        "components": [
            "Navigation menu",
            "Footer component",
            "Form components",
            "Modal dialogs",
            "Loading indicators",
            "Error pages (404, 500)",
        ],
        "assets": [
            "Logo and branding assets",
            "Icon library",
            "Stock photography/images",
            "CSS stylesheets", 
            "JavaScript modules",
            "Font files",
        ],
    },
    "backend": {
        "apis": [
            "Authentication API",
            "User management API",
            "Data CRUD APIs",
            "File upload API",
            "Notification API",
            "Reporting API",
        ],
        "databases": [
            "User accounts table",
            "Application data tables",
            "Audit/logging tables",
            "Configuration tables",
            "Session storage",
        ],
        "services": [
            "Email service integration",
            "Payment processing service",
            "File storage service",
            "Backup/recovery service",
            "Monitoring service",
        ],
    },
    "documentation": {
        "technical": [
            "API documentation",
            "Database schema documentation", 
            "Deployment guide",
            "Architecture overview",
            "Security documentation",
        ],
        "user": [
            "User manual/guide",
            "Admin documentation",
            "FAQ section",
            "Tutorial content",
            "Release notes",
        ],
    },
    "infrastructure": {
        "hosting": [
            "Web server configuration",
            "Database server setup",
            "CDN configuration",
            "SSL certificate",
            "Domain setup",
        ],
        "monitoring": [
            "Application monitoring",
            "Performance tracking",
            "Error logging system",
            "Backup monitoring",
            "Security monitoring",
        ],
    },
}

BUSINESS_TYPE_ASSETS = {
    "ecommerce": [
        "Product catalog database",
        "Shopping cart functionality",
        "Payment gateway integration",
        "Order management system",
        "Inventory tracking system",
        "Customer review system",
    ],
    "healthcare": [
        "Patient data management",
        "HIPAA compliance documentation",
        "Appointment scheduling system",
        "Medical records integration",
        "Insurance verification system",
    ],
    "fintech": [
        "Financial data APIs", 
        "Compliance documentation",
        "Transaction processing system",
        "Fraud detection system",
        "Audit trail system",
    ],
    "education": [
        "Course content management",
        "Student progress tracking",
        "Assignment submission system",
        "Grade book integration",
        "Learning analytics",
    ],
}


def get_tool_metadata() -> dict[str, Any]:
    """Get metadata for the asset extraction tool."""
    return {
        "name": "extract_assets",
        "description": "Extract and catalog project assets from requirements analysis",
        "version": "1.0.0",
        "category": "analysis",
        "parameters": {
            "type": "object",
            "properties": {
                "requirements": {
                    "type": "object",
                    "description": "Requirements analysis results",
                },
                "business_context": {
                    "type": "object",
                    "description": "Business type and project context",
                    "default": {},
                },
                "scope_level": {
                    "type": "string",
                    "enum": ["minimal", "standard", "comprehensive"],
                    "description": "Scope level for asset extraction",
                    "default": "standard",
                },
            },
            "required": ["requirements"],
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "frontend_assets": {
                    "type": "array",
                    "description": "Frontend components and resources",
                },
                "backend_assets": {
                    "type": "array",
                    "description": "Backend services and data structures",
                },
                "documentation_assets": {
                    "type": "array",
                    "description": "Documentation deliverables",
                },
                "infrastructure_assets": {
                    "type": "array",
                    "description": "Infrastructure and deployment assets",
                },
                "asset_summary": {
                    "type": "object",
                    "description": "Summary of total assets by category",
                },
            },
        },
        "dependencies": [],
    }


def run(parameters: dict[str, Any]) -> dict[str, Any]:
    """
    Extract project assets from requirements analysis.
    
    Args:
        parameters: Tool execution parameters
        
    Returns:
        Dictionary containing categorized project assets
    """
    requirements = parameters.get("requirements", {})
    business_context = parameters.get("business_context", {})
    scope_level = parameters.get("scope_level", "standard")
    
    if not requirements:
        return {
            "error": "No requirements provided for asset extraction",
            "frontend_assets": [],
            "backend_assets": [],
            "documentation_assets": [], 
            "infrastructure_assets": [],
            "asset_summary": {},
        }
    
    logger.info("Extracting assets with %s scope level", scope_level)
    
    business_type = business_context.get("business_type", "general")
    
    # Extract assets by category
    frontend_assets = _extract_frontend_assets(requirements, scope_level)
    backend_assets = _extract_backend_assets(requirements, business_type, scope_level)
    documentation_assets = _extract_documentation_assets(requirements, scope_level)
    infrastructure_assets = _extract_infrastructure_assets(requirements, scope_level)
    
    # Add business-specific assets
    business_assets = _extract_business_specific_assets(business_type, requirements)
    backend_assets.extend(business_assets)
    
    # Create asset summary
    asset_summary = {
        "frontend_count": len(frontend_assets),
        "backend_count": len(backend_assets),
        "documentation_count": len(documentation_assets),
        "infrastructure_count": len(infrastructure_assets),
        "total_count": len(frontend_assets) + len(backend_assets) + 
                      len(documentation_assets) + len(infrastructure_assets),
        "scope_level": scope_level,
        "business_type": business_type,
    }
    
    return {
        "frontend_assets": frontend_assets,
        "backend_assets": backend_assets,
        "documentation_assets": documentation_assets,
        "infrastructure_assets": infrastructure_assets,
        "asset_summary": asset_summary,
        "extraction_metadata": {
            "tool": "extract_assets",
            "version": "1.0.0",
            "scope_level": scope_level,
            "business_type": business_type,
        },
    }


def _extract_frontend_assets(requirements: dict[str, Any], scope_level: str) -> list[dict[str, Any]]:
    """Extract frontend assets based on requirements."""
    assets = []
    
    functional_reqs = requirements.get("functional_requirements", [])
    
    # Check for web interface requirements
    has_web_interface = any("web" in req.get("category", "").lower() for req in functional_reqs)
    has_user_auth = any("auth" in req.get("category", "").lower() for req in functional_reqs)
    has_data_management = any("data" in req.get("category", "").lower() for req in functional_reqs)
    
    if has_web_interface or scope_level != "minimal":
        # Basic web pages
        for page in ASSET_TEMPLATES["frontend"]["web_pages"][:4]:
            assets.append({
                "name": page,
                "category": "web_page",
                "priority": "high" if page == "Homepage/Landing page" else "medium",
                "estimated_effort": "medium",
            })
    
    if has_user_auth:
        # Authentication pages
        auth_pages = ["Login/Registration pages", "User dashboard"]
        for page in auth_pages:
            assets.append({
                "name": page,
                "category": "web_page",
                "priority": "high",
                "estimated_effort": "medium",
            })
    
    # Essential components
    components = ASSET_TEMPLATES["frontend"]["components"]
    if scope_level == "minimal":
        components = components[:3]
    elif scope_level == "comprehensive":
        components = components  # All components
    else:
        components = components[:4]  # Standard scope
    
    for component in components:
        assets.append({
            "name": component,
            "category": "component",
            "priority": "medium",
            "estimated_effort": "small",
        })
    
    # Visual assets
    for asset in ASSET_TEMPLATES["frontend"]["assets"][:4]:
        assets.append({
            "name": asset,
            "category": "visual_asset",
            "priority": "medium",
            "estimated_effort": "small",
        })
    
    return assets


def _extract_backend_assets(
    requirements: dict[str, Any], 
    business_type: str, 
    scope_level: str,
) -> list[dict[str, Any]]:
    """Extract backend assets based on requirements."""
    assets = []
    
    functional_reqs = requirements.get("functional_requirements", [])
    technical_reqs = requirements.get("technical_requirements", [])
    
    # Check requirement categories
    has_auth = any("auth" in req.get("category", "").lower() for req in functional_reqs)
    has_data = any("data" in req.get("category", "").lower() for req in functional_reqs)
    has_api_needs = any(req.get("category") == "web" for req in technical_reqs)
    
    if has_auth or scope_level != "minimal":
        # Authentication API
        assets.append({
            "name": "Authentication API",
            "category": "api",
            "priority": "high",
            "estimated_effort": "large",
        })
    
    if has_data or scope_level != "minimal":
        # Data APIs
        for api in ASSET_TEMPLATES["backend"]["apis"][1:4]:  # Skip auth API (already added)
            assets.append({
                "name": api,
                "category": "api", 
                "priority": "high",
                "estimated_effort": "medium",
            })
    
    # Database components
    if has_data or has_auth:
        for db_component in ASSET_TEMPLATES["backend"]["databases"][:3]:
            assets.append({
                "name": db_component,
                "category": "database",
                "priority": "high", 
                "estimated_effort": "medium",
            })
    
    # Essential services
    service_count = 2 if scope_level == "minimal" else 4 if scope_level == "standard" else 5
    for service in ASSET_TEMPLATES["backend"]["services"][:service_count]:
        assets.append({
            "name": service,
            "category": "service",
            "priority": "medium",
            "estimated_effort": "large",
        })
    
    return assets


def _extract_documentation_assets(requirements: dict[str, Any], scope_level: str) -> list[dict[str, Any]]:
    """Extract documentation assets."""
    assets = []
    
    # Technical documentation
    tech_docs = ASSET_TEMPLATES["documentation"]["technical"]
    if scope_level == "minimal":
        tech_docs = tech_docs[:2]
    elif scope_level == "comprehensive":
        tech_docs = tech_docs  # All documentation
    else:
        tech_docs = tech_docs[:3]  # Standard scope
    
    for doc in tech_docs:
        assets.append({
            "name": doc,
            "category": "technical_documentation",
            "priority": "medium",
            "estimated_effort": "medium",
        })
    
    # User documentation
    user_docs = ASSET_TEMPLATES["documentation"]["user"][:2]  # Always include basic user docs
    if scope_level == "comprehensive":
        user_docs = ASSET_TEMPLATES["documentation"]["user"]
    
    for doc in user_docs:
        assets.append({
            "name": doc,
            "category": "user_documentation",
            "priority": "medium",
            "estimated_effort": "small",
        })
    
    return assets


def _extract_infrastructure_assets(requirements: dict[str, Any], scope_level: str) -> list[dict[str, Any]]:
    """Extract infrastructure and deployment assets."""
    assets = []
    
    # Essential hosting components
    hosting_components = ASSET_TEMPLATES["infrastructure"]["hosting"]
    if scope_level == "minimal":
        hosting_components = hosting_components[:3]
    
    for component in hosting_components:
        assets.append({
            "name": component,
            "category": "hosting",
            "priority": "high",
            "estimated_effort": "medium",
        })
    
    # Monitoring components
    if scope_level != "minimal":
        monitoring_components = ASSET_TEMPLATES["infrastructure"]["monitoring"][:3]
        if scope_level == "comprehensive":
            monitoring_components = ASSET_TEMPLATES["infrastructure"]["monitoring"]
        
        for component in monitoring_components:
            assets.append({
                "name": component,
                "category": "monitoring",
                "priority": "medium",
                "estimated_effort": "small",
            })
    
    return assets


def _extract_business_specific_assets(business_type: str, requirements: dict[str, Any]) -> list[dict[str, Any]]:
    """Extract business-type specific assets."""
    assets = []
    
    if business_type in BUSINESS_TYPE_ASSETS:
        specific_assets = BUSINESS_TYPE_ASSETS[business_type]
        
        for asset_name in specific_assets:
            assets.append({
                "name": asset_name,
                "category": "business_specific",
                "priority": "high",
                "estimated_effort": "large",
                "business_type": business_type,
            })
    
    return assets
