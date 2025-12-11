"""
Deterministic missing component detection tool.

This tool analyzes project assets and requirements to identify potential
gaps, missing components, or inconsistencies using rule-based analysis.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Critical component dependencies
COMPONENT_DEPENDENCIES = {
    "frontend": {
        "web_pages": {
            "requires": ["Navigation menu", "CSS stylesheets"],
            "optional": ["Footer component", "Error pages (404, 500)"],
        },
        "user_auth": {
            "requires": ["Login/Registration pages", "Authentication API", "User accounts table"],
            "optional": ["User dashboard", "Session storage"],
        },
        "forms": {
            "requires": ["Form components", "Validation system"],
            "optional": ["Modal dialogs", "Loading indicators"],
        },
    },
    "backend": {
        "api_system": {
            "requires": ["Authentication API", "Error handling", "Request validation"],
            "optional": ["Rate limiting", "API documentation"],
        },
        "data_persistence": {
            "requires": ["Database setup", "Data models", "Migration system"],
            "optional": ["Backup system", "Data validation"],
        },
        "user_management": {
            "requires": ["User accounts table", "Authentication API", "Session management"],
            "optional": ["User roles system", "Profile management"],
        },
    },
    "infrastructure": {
        "production_deployment": {
            "requires": ["Web server configuration", "SSL certificate", "Domain setup"],
            "optional": ["CDN configuration", "Load balancing"],
        },
        "monitoring": {
            "requires": ["Error logging system", "Application monitoring"],
            "optional": ["Performance tracking", "Security monitoring"],
        },
    },
}

# Common missing components by project type
COMMON_GAPS = {
    "security": [
        "Input validation system",
        "CSRF protection",
        "SQL injection prevention", 
        "XSS protection",
        "Rate limiting",
        "Security headers configuration",
    ],
    "performance": [
        "Database indexing strategy",
        "Caching layer",
        "Image optimization",
        "Code minification",
        "Lazy loading implementation",
    ],
    "user_experience": [
        "Loading states", 
        "Error handling UI",
        "Mobile responsiveness",
        "Accessibility features",
        "Progressive web app features",
    ],
    "operations": [
        "Deployment pipeline",
        "Environment configuration",
        "Database migration system",
        "Backup and recovery procedures",
        "Health check endpoints",
    ],
    "testing": [
        "Unit test suite",
        "Integration tests",
        "End-to-end tests",
        "Performance tests",
        "Security tests",
    ],
}

# Business type specific requirements
BUSINESS_SPECIFIC_REQUIREMENTS = {
    "ecommerce": [
        "Payment gateway integration",
        "Shopping cart persistence",
        "Inventory management",
        "Order tracking system",
        "Product search functionality",
    ],
    "healthcare": [
        "HIPAA compliance measures",
        "Patient data encryption",
        "Audit trail system",
        "Access control system",
        "Data retention policies",
    ],
    "fintech": [
        "Financial regulations compliance",
        "Transaction security",
        "Fraud detection system",
        "Audit logging",
        "Data encryption at rest",
    ],
    "education": [
        "Student data privacy",
        "Grade book security",
        "Content delivery system",
        "Progress tracking",
        "Assignment submission system",
    ],
}


def get_tool_metadata() -> dict[str, Any]:
    """Get metadata for the missing component detection tool."""
    return {
        "name": "detect_missing",
        "description": "Detect missing components and gaps in project scope",
        "version": "1.0.0",
        "category": "analysis",
        "parameters": {
            "type": "object",
            "properties": {
                "assets": {
                    "type": "object",
                    "description": "Project assets from extract_assets tool",
                },
                "requirements": {
                    "type": "object", 
                    "description": "Requirements analysis results",
                },
                "business_context": {
                    "type": "object",
                    "description": "Business type and project context",
                    "default": {},
                },
                "analysis_depth": {
                    "type": "string",
                    "enum": ["basic", "standard", "comprehensive"],
                    "description": "Depth of gap analysis",
                    "default": "standard",
                },
            },
            "required": ["assets", "requirements"],
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "critical_gaps": {
                    "type": "array",
                    "description": "Critical missing components that block functionality",
                },
                "recommended_additions": {
                    "type": "array", 
                    "description": "Recommended components to improve the project",
                },
                "dependency_issues": {
                    "type": "array",
                    "description": "Components with missing dependencies",
                },
                "business_specific_gaps": {
                    "type": "array",
                    "description": "Missing components specific to business type",
                },
                "gap_summary": {
                    "type": "object",
                    "description": "Summary of identified gaps and issues",
                },
            },
        },
        "dependencies": ["extract_assets"],
    }


def run(parameters: dict[str, Any]) -> dict[str, Any]:
    """
    Detect missing components and gaps in project scope.
    
    Args:
        parameters: Tool execution parameters
        
    Returns:
        Dictionary containing identified gaps and missing components
    """
    assets = parameters.get("assets", {})
    requirements = parameters.get("requirements", {})
    business_context = parameters.get("business_context", {})
    analysis_depth = parameters.get("analysis_depth", "standard")
    
    if not assets or not requirements:
        return {
            "error": "Assets and requirements must be provided for gap detection",
            "critical_gaps": [],
            "recommended_additions": [],
            "dependency_issues": [],
            "business_specific_gaps": [],
            "gap_summary": {},
        }
    
    logger.info("Detecting gaps with %s analysis depth", analysis_depth)
    
    business_type = business_context.get("business_type", "general")
    
    # Analyze different types of gaps
    critical_gaps = _detect_critical_gaps(assets, requirements)
    dependency_issues = _check_dependencies(assets)
    recommended_additions = _identify_recommendations(assets, requirements, analysis_depth)
    business_gaps = _check_business_specific_gaps(assets, business_type)
    
    # Create gap summary
    gap_summary = {
        "critical_count": len(critical_gaps),
        "dependency_issues_count": len(dependency_issues),
        "recommended_count": len(recommended_additions),
        "business_gaps_count": len(business_gaps),
        "total_gaps": len(critical_gaps) + len(dependency_issues) + len(business_gaps),
        "analysis_depth": analysis_depth,
        "risk_level": _calculate_risk_level(critical_gaps, dependency_issues),
    }
    
    return {
        "critical_gaps": critical_gaps,
        "recommended_additions": recommended_additions,
        "dependency_issues": dependency_issues,
        "business_specific_gaps": business_gaps,
        "gap_summary": gap_summary,
        "detection_metadata": {
            "tool": "detect_missing",
            "version": "1.0.0",
            "analysis_depth": analysis_depth,
            "business_type": business_type,
        },
    }


def _detect_critical_gaps(assets: dict[str, Any], requirements: dict[str, Any]) -> list[dict[str, Any]]:
    """Detect critical gaps that would block core functionality."""
    gaps = []
    
    # Extract asset names by category
    asset_names = _extract_asset_names(assets)
    
    # Check for authentication requirements vs assets
    functional_reqs = requirements.get("functional_requirements", [])
    has_auth_req = any("auth" in req.get("category", "").lower() for req in functional_reqs)
    
    if has_auth_req:
        if "Authentication API" not in asset_names:
            gaps.append({
                "component": "Authentication API",
                "category": "backend",
                "severity": "critical",
                "reason": "Authentication required but no API defined",
                "impact": "Users cannot log in or access secure features",
            })
        
        if "User accounts table" not in asset_names:
            gaps.append({
                "component": "User accounts table",
                "category": "database",
                "severity": "critical", 
                "reason": "Authentication requires user data storage",
                "impact": "Cannot store user credentials or profile data",
            })
    
    # Check for data management requirements
    has_data_req = any("data" in req.get("category", "").lower() for req in functional_reqs)
    if has_data_req:
        if not any("database" in name.lower() for name in asset_names):
            gaps.append({
                "component": "Database system",
                "category": "infrastructure",
                "severity": "critical",
                "reason": "Data management required but no database defined",
                "impact": "Cannot persist application data",
            })
    
    # Check for web interface requirements
    has_web_req = any("web" in req.get("category", "").lower() for req in functional_reqs)
    if has_web_req:
        if not any("page" in name.lower() for name in asset_names):
            gaps.append({
                "component": "Web pages",
                "category": "frontend", 
                "severity": "critical",
                "reason": "Web interface required but no pages defined",
                "impact": "Users cannot access the application",
            })
    
    # Check for security fundamentals
    if not any("ssl" in name.lower() or "certificate" in name.lower() for name in asset_names):
        gaps.append({
            "component": "SSL Certificate",
            "category": "security",
            "severity": "critical",
            "reason": "HTTPS is essential for production deployment",
            "impact": "Insecure data transmission, browser warnings",
        })
    
    return gaps


def _check_dependencies(assets: dict[str, Any]) -> list[dict[str, Any]]:
    """Check for missing dependencies between components."""
    dependency_issues = []
    
    asset_names = _extract_asset_names(assets)
    
    # Check each dependency category
    for category, dependencies in COMPONENT_DEPENDENCIES.items():
        for component_type, deps in dependencies.items():
            # Check if we have components of this type
            has_component_type = _has_component_type(asset_names, component_type)
            
            if has_component_type:
                # Check required dependencies
                for required in deps.get("requires", []):
                    if required not in asset_names:
                        dependency_issues.append({
                            "component": component_type,
                            "missing_dependency": required,
                            "category": category,
                            "severity": "high",
                            "reason": f"{component_type} requires {required}",
                            "impact": "Component may not function properly",
                        })
    
    return dependency_issues


def _identify_recommendations(
    assets: dict[str, Any], 
    requirements: dict[str, Any], 
    analysis_depth: str,
) -> list[dict[str, Any]]:
    """Identify recommended additions to improve the project."""
    recommendations = []
    
    asset_names = _extract_asset_names(assets)
    
    # Determine which gap categories to check based on analysis depth
    categories_to_check = ["security", "user_experience"]
    if analysis_depth in ["standard", "comprehensive"]:
        categories_to_check.extend(["performance", "operations"])
    if analysis_depth == "comprehensive":
        categories_to_check.append("testing")
    
    # Check each category for missing components
    for category in categories_to_check:
        for component in COMMON_GAPS[category]:
            if not any(component.lower() in name.lower() for name in asset_names):
                recommendations.append({
                    "component": component,
                    "category": category,
                    "priority": _get_recommendation_priority(category, component),
                    "reason": f"Improves {category} aspects of the application",
                    "benefit": _get_component_benefit(category, component),
                })
    
    return recommendations


def _check_business_specific_gaps(assets: dict[str, Any], business_type: str) -> list[dict[str, Any]]:
    """Check for missing business-type specific components."""
    gaps = []
    
    if business_type not in BUSINESS_SPECIFIC_REQUIREMENTS:
        return gaps
    
    asset_names = _extract_asset_names(assets)
    required_components = BUSINESS_SPECIFIC_REQUIREMENTS[business_type]
    
    for component in required_components:
        if not any(component.lower() in name.lower() for name in asset_names):
            gaps.append({
                "component": component,
                "category": "business_specific",
                "business_type": business_type,
                "severity": "high",
                "reason": f"Required for {business_type} business operations",
                "impact": "May not meet industry standards or regulations",
            })
    
    return gaps


def _extract_asset_names(assets: dict[str, Any]) -> list[str]:
    """Extract all asset names from the assets structure."""
    names = []
    
    for category in ["frontend_assets", "backend_assets", "documentation_assets", "infrastructure_assets"]:
        asset_list = assets.get(category, [])
        for asset in asset_list:
            if isinstance(asset, dict) and "name" in asset:
                names.append(asset["name"])
            elif isinstance(asset, str):
                names.append(asset)
    
    return names


def _has_component_type(asset_names: list[str], component_type: str) -> bool:
    """Check if assets include components of a specific type."""
    type_keywords = {
        "web_pages": ["page", "homepage", "dashboard"],
        "user_auth": ["auth", "login", "registration", "user"],
        "forms": ["form", "input", "submit"],
        "api_system": ["api", "endpoint", "service"],
        "data_persistence": ["database", "table", "model", "storage"],
        "user_management": ["user", "account", "profile"],
        "production_deployment": ["server", "deployment", "hosting"],
        "monitoring": ["monitor", "logging", "tracking"],
    }
    
    keywords = type_keywords.get(component_type, [])
    return any(
        keyword in name.lower() 
        for keyword in keywords 
        for name in asset_names
    )


def _get_recommendation_priority(category: str, component: str) -> str:
    """Get priority level for a recommended component."""
    high_priority = ["Input validation system", "Error handling UI", "Health check endpoints"]
    
    if component in high_priority:
        return "high"
    elif category in ["security", "operations"]:
        return "high" 
    elif category == "user_experience":
        return "medium"
    else:
        return "low"


def _get_component_benefit(category: str, component: str) -> str:
    """Get the benefit description for a component."""
    benefits = {
        "security": "Protects against common vulnerabilities and attacks",
        "performance": "Improves application speed and user experience", 
        "user_experience": "Enhances usability and accessibility",
        "operations": "Improves deployment and maintenance procedures",
        "testing": "Ensures code quality and prevents regressions",
    }
    
    return benefits.get(category, "Improves overall application quality")


def _calculate_risk_level(critical_gaps: list[dict[str, Any]], dependency_issues: list[dict[str, Any]]) -> str:
    """Calculate overall risk level based on gaps."""
    critical_count = len(critical_gaps)
    dependency_count = len(dependency_issues)
    
    if critical_count >= 3 or dependency_count >= 5:
        return "high"
    elif critical_count >= 1 or dependency_count >= 3:
        return "medium"
    else:
        return "low"
