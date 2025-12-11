"""
Deterministic requirement expansion tool.

This tool expands basic requirements into detailed specifications using 
rule-based logic and templates rather than LLM calls.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)


def get_tool_metadata() -> dict[str, Any]:
    """Get metadata for the requirement expansion tool."""
    return {
        "name": "expand_requirements", 
        "description": "Expand basic requirements into detailed specifications using templates",
        "version": "1.0.0",
        "category": "intake",
        "parameters": {
            "type": "object",
            "properties": {
                "requirements": {
                    "type": "array",
                    "description": "List of basic requirements to expand",
                    "items": {"type": "object"},
                },
                "business_type": {
                    "type": "string",
                    "description": "Business type for context-specific expansion",
                    "default": "general",
                },
                "client_tier": {
                    "type": "string",
                    "enum": ["starter", "business", "premium"],
                    "description": "Client tier for scope complexity",
                    "default": "business",
                },
            },
            "required": ["requirements"],
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "expanded_requirements": {
                    "type": "array",
                    "description": "Detailed requirement specifications",
                },
                "technical_implications": {
                    "type": "array", 
                    "description": "Technical considerations and dependencies",
                },
                "estimated_complexity": {
                    "type": "string",
                    "enum": ["low", "medium", "high"],
                },
            },
        },
        "dependencies": ["mcp_servers.skills.validators"],
    }


def run(parameters: dict[str, Any]) -> dict[str, Any]:
    """
    Expand basic requirements into detailed specifications.
    
    Args:
        parameters: Tool execution parameters containing requirements to expand
        
    Returns:
        Dictionary with expanded requirements and technical implications
    """
    requirements = parameters.get("requirements", [])
    business_type = parameters.get("business_type", "general")
    client_tier = parameters.get("client_tier", "business")
    
    logger.info("Expanding %d requirements for %s business", len(requirements), business_type)
    
    expanded_requirements = []
    technical_implications = []
    complexity_scores = []
    
    for req in requirements:
        req_type = req.get("type", "unknown")
        confidence = req.get("confidence", 0.5)
        
        # Expand based on requirement type
        if req_type == "website":
            expanded = _expand_website_requirements(req, business_type, client_tier)
        elif req_type == "mobile_app":
            expanded = _expand_mobile_app_requirements(req, business_type, client_tier)
        elif req_type == "backend":
            expanded = _expand_backend_requirements(req, business_type, client_tier)
        elif req_type == "ecommerce":
            expanded = _expand_ecommerce_requirements(req, business_type, client_tier)
        elif req_type == "integration":
            expanded = _expand_integration_requirements(req, business_type, client_tier)
        elif req_type == "cms":
            expanded = _expand_cms_requirements(req, business_type, client_tier)
        else:
            expanded = _expand_generic_requirements(req, business_type, client_tier)
        
        expanded_requirements.append(expanded)
        technical_implications.extend(expanded.get("technical_considerations", []))
        complexity_scores.append(expanded.get("complexity_score", 2))
    
    # Calculate overall complexity
    avg_complexity = sum(complexity_scores) / len(complexity_scores) if complexity_scores else 2
    complexity_level = "low" if avg_complexity < 2 else "high" if avg_complexity > 3 else "medium"
    
    return {
        "expanded_requirements": expanded_requirements,
        "technical_implications": list(set(technical_implications)),  # Remove duplicates
        "estimated_complexity": complexity_level,
        "processing_metadata": {
            "tool": "expand_requirements",
            "version": "1.0.0",
            "business_type": business_type,
            "client_tier": client_tier,
            "original_count": len(requirements),
        },
    }


def _expand_website_requirements(req: dict[str, Any], business_type: str, client_tier: str) -> dict[str, Any]:
    """Expand website requirements based on templates."""
    
    # Base website components
    components = [
        "Homepage with company overview",
        "About page with team information", 
        "Services/Products pages",
        "Contact page with form",
        "Responsive design for mobile/tablet",
    ]
    
    # Business-specific additions
    if business_type == "ecommerce":
        components.extend([
            "Product catalog with search/filtering",
            "Shopping cart functionality",
            "Payment processing integration",
            "User account management",
            "Order tracking system",
        ])
    elif business_type == "healthcare":
        components.extend([
            "Patient portal with secure login",
            "Appointment scheduling system",
            "HIPAA-compliant forms",
            "Insurance information portal",
        ])
    elif business_type == "education":
        components.extend([
            "Course catalog and descriptions",
            "Student enrollment system",
            "Learning management integration",
            "Faculty/staff directory",
        ])
    
    # Tier-based complexity
    if client_tier == "premium":
        components.extend([
            "Advanced analytics dashboard",
            "A/B testing framework", 
            "Multi-language support",
            "Advanced SEO optimization",
        ])
    elif client_tier == "starter":
        components = components[:5]  # Basic components only
    
    # Technical considerations
    tech_considerations = [
        "Content Management System (CMS)",
        "SSL certificate for security",
        "Search Engine Optimization (SEO)",
        "Website performance optimization",
        "Cross-browser compatibility testing",
    ]
    
    if business_type in ["ecommerce", "healthcare", "fintech"]:
        tech_considerations.append("Enhanced security measures")
        tech_considerations.append("Data encryption requirements")
    
    complexity_score = 2 + len([c for c in components if "integration" in c.lower()]) * 0.5
    
    return {
        "type": "website",
        "title": f"{business_type.title()} Website Development",
        "components": components,
        "technical_considerations": tech_considerations,
        "estimated_timeline": _calculate_timeline(len(components), client_tier),
        "complexity_score": min(5, complexity_score),
        "original_confidence": req.get("confidence", 0.5),
    }


def _expand_mobile_app_requirements(req: dict[str, Any], business_type: str, client_tier: str) -> dict[str, Any]:
    """Expand mobile app requirements."""
    
    # Base app features
    features = [
        "User authentication and profiles",
        "Core app functionality screens",
        "Push notifications",
        "Offline data synchronization",
        "App store deployment",
    ]
    
    # Business-specific features
    if business_type == "ecommerce":
        features.extend([
            "Product browsing and search",
            "Shopping cart and checkout",
            "Payment gateway integration",
            "Order history and tracking",
        ])
    elif business_type == "healthcare":
        features.extend([
            "Appointment scheduling",
            "Prescription management",
            "Health data tracking",
            "Secure messaging with providers",
        ])
    elif business_type == "fintech":
        features.extend([
            "Account balance and transactions",
            "Money transfer capabilities", 
            "Investment portfolio tracking",
            "Security features (2FA, biometrics)",
        ])
    
    # Platform considerations
    platforms = ["iOS", "Android"]
    if client_tier == "starter":
        platforms = ["iOS or Android (single platform)"]
    
    tech_considerations = [
        "Native vs cross-platform development decision",
        "Backend API integration",
        "App store compliance requirements",
        "Device testing across multiple models",
        "Performance optimization",
    ]
    
    if business_type in ["healthcare", "fintech"]:
        tech_considerations.append("Enhanced security and compliance")
        tech_considerations.append("Data encryption and secure storage")
    
    complexity_score = 3 + len(features) * 0.1
    
    return {
        "type": "mobile_app",
        "title": f"{business_type.title()} Mobile Application",
        "features": features,
        "platforms": platforms,
        "technical_considerations": tech_considerations,
        "estimated_timeline": _calculate_timeline(len(features) * 2, client_tier),  # Mobile is more complex
        "complexity_score": min(5, complexity_score),
        "original_confidence": req.get("confidence", 0.5),
    }


def _expand_backend_requirements(req: dict[str, Any], business_type: str, client_tier: str) -> dict[str, Any]:
    """Expand backend/API requirements."""
    
    # Base backend components
    components = [
        "Database design and implementation",
        "RESTful API development",
        "User authentication system",
        "Data validation and processing",
        "Error handling and logging",
    ]
    
    # Business-specific backend needs
    if business_type == "ecommerce":
        components.extend([
            "Product inventory management",
            "Order processing system",
            "Payment processing integration",
            "Shipping calculation engine",
        ])
    elif business_type == "fintech":
        components.extend([
            "Transaction processing system",
            "Fraud detection mechanisms", 
            "Regulatory compliance features",
            "Audit trail implementation",
        ])
    elif business_type == "healthcare":
        components.extend([
            "Patient data management",
            "HIPAA compliance features",
            "Appointment scheduling system",
            "Medical records integration",
        ])
    
    # Tier-based scaling
    if client_tier == "premium":
        components.extend([
            "Advanced analytics and reporting",
            "Real-time data processing",
            "Microservices architecture",
            "Auto-scaling infrastructure",
        ])
    
    tech_considerations = [
        "Database selection (SQL vs NoSQL)",
        "Server infrastructure and hosting",
        "API security and rate limiting",
        "Data backup and recovery",
        "Performance monitoring",
    ]
    
    complexity_score = 3.5 + len([c for c in components if "integration" in c.lower()]) * 0.3
    
    return {
        "type": "backend",
        "title": f"{business_type.title()} Backend System",
        "components": components,
        "technical_considerations": tech_considerations,
        "estimated_timeline": _calculate_timeline(len(components) * 1.5, client_tier),
        "complexity_score": min(5, complexity_score),
        "original_confidence": req.get("confidence", 0.5),
    }


def _expand_ecommerce_requirements(req: dict[str, Any], business_type: str, client_tier: str) -> dict[str, Any]:
    """Expand e-commerce specific requirements."""
    
    # Core e-commerce features
    features = [
        "Product catalog management",
        "Shopping cart and checkout",
        "Payment gateway integration",
        "Order management system",
        "Customer account management",
        "Inventory tracking",
    ]
    
    # Tier-based feature additions
    if client_tier == "premium":
        features.extend([
            "Advanced product recommendations",
            "Multi-vendor marketplace support",
            "Subscription management",
            "Advanced analytics dashboard",
            "Marketing automation tools",
        ])
    elif client_tier == "business":
        features.extend([
            "Basic product recommendations",
            "Coupon and discount system", 
            "Customer reviews and ratings",
            "Email notifications",
        ])
    
    # Industry-specific considerations
    if business_type == "fashion":
        features.extend(["Size/color variants", "Wishlist functionality"])
    elif business_type == "food":
        features.extend(["Delivery tracking", "Nutritional information"])
    
    tech_considerations = [
        "PCI DSS compliance for payments",
        "SSL certificate and security",
        "Performance optimization for scale",
        "Mobile responsiveness",
        "Search engine optimization",
        "Third-party integrations (shipping, taxes)",
    ]
    
    complexity_score = 4 + len(features) * 0.1
    
    return {
        "type": "ecommerce",
        "title": "E-commerce Platform",
        "features": features,
        "technical_considerations": tech_considerations,
        "estimated_timeline": _calculate_timeline(len(features) * 1.8, client_tier),
        "complexity_score": min(5, complexity_score),
        "original_confidence": req.get("confidence", 0.5),
    }


def _expand_integration_requirements(req: dict[str, Any], business_type: str, client_tier: str) -> dict[str, Any]:
    """Expand system integration requirements."""
    
    # Common integration types
    integrations = [
        "Third-party API connections",
        "Data synchronization between systems", 
        "Authentication system integration",
        "Webhook implementation for real-time updates",
    ]
    
    # Business-specific integrations
    if business_type == "ecommerce":
        integrations.extend([
            "Payment processor integration",
            "Shipping provider APIs",
            "Inventory management system",
            "Customer relationship management (CRM)",
        ])
    elif business_type == "healthcare":
        integrations.extend([
            "Electronic Health Record (EHR) systems",
            "Insurance verification APIs",
            "Lab result systems",
            "Prescription management systems",
        ])
    elif business_type == "fintech":
        integrations.extend([
            "Banking API connections",
            "Credit reporting services",
            "Regulatory reporting systems",
            "Identity verification services",
        ])
    
    tech_considerations = [
        "API rate limiting and error handling",
        "Data mapping and transformation",
        "Security and authentication protocols",
        "Monitoring and logging integration health",
        "Fallback mechanisms for system failures",
    ]
    
    complexity_score = 3.5 + len(integrations) * 0.2
    
    return {
        "type": "integration",
        "title": "System Integration Services",
        "integrations": integrations,
        "technical_considerations": tech_considerations,
        "estimated_timeline": _calculate_timeline(len(integrations) * 2, client_tier),
        "complexity_score": min(5, complexity_score),
        "original_confidence": req.get("confidence", 0.5),
    }


def _expand_cms_requirements(req: dict[str, Any], business_type: str, client_tier: str) -> dict[str, Any]:
    """Expand content management system requirements."""
    
    # Base CMS features
    features = [
        "Content creation and editing interface",
        "User role and permission management",
        "Media library and file management",
        "Content publishing workflow",
        "SEO optimization tools",
    ]
    
    # Business-specific CMS features
    if business_type == "news" or business_type == "media":
        features.extend([
            "Article scheduling and publication",
            "Comment moderation system",
            "Newsletter integration",
            "Social media publishing",
        ])
    elif business_type == "education":
        features.extend([
            "Course content management",
            "Student progress tracking",
            "Assignment submission system",
            "Grade book integration",
        ])
    
    # Tier-based features
    if client_tier == "premium":
        features.extend([
            "Advanced content analytics",
            "A/B testing for content",
            "Multi-language content support",
            "Advanced workflow automation",
        ])
    
    tech_considerations = [
        "Database design for content storage",
        "Caching strategy for performance",
        "Content delivery network (CDN) integration",
        "Backup and version control",
        "Security measures for content protection",
    ]
    
    complexity_score = 2.5 + len(features) * 0.15
    
    return {
        "type": "cms",
        "title": "Content Management System",
        "features": features,
        "technical_considerations": tech_considerations,
        "estimated_timeline": _calculate_timeline(len(features) * 1.3, client_tier),
        "complexity_score": min(5, complexity_score),
        "original_confidence": req.get("confidence", 0.5),
    }


def _expand_generic_requirements(req: dict[str, Any], business_type: str, client_tier: str) -> dict[str, Any]:
    """Expand generic/unknown requirements with basic template."""
    
    # Generic software features
    features = [
        "User interface design and implementation",
        "Basic functionality implementation",
        "Data storage and retrieval",
        "User authentication (if needed)",
        "Basic reporting capabilities",
    ]
    
    # Adjust based on client tier
    if client_tier == "premium":
        features.extend([
            "Advanced analytics and insights",
            "Integration capabilities",
            "Custom workflow features",
        ])
    elif client_tier == "starter":
        features = features[:3]  # Keep it simple
    
    tech_considerations = [
        "Technology stack selection",
        "Architecture design decisions",
        "Security implementation",
        "Performance optimization",
        "Testing and quality assurance",
    ]
    
    return {
        "type": req.get("type", "custom"),
        "title": f"Custom {business_type.title()} Solution",
        "features": features,
        "technical_considerations": tech_considerations,
        "estimated_timeline": _calculate_timeline(len(features), client_tier),
        "complexity_score": 2.5,
        "original_confidence": req.get("confidence", 0.5),
        "note": "Generic expansion - requires more detailed requirements gathering",
    }


def _calculate_timeline(feature_count: int, client_tier: str) -> str:
    """Calculate estimated timeline based on feature count and complexity."""
    
    # Base timeline calculation (weeks)
    base_weeks = feature_count * 0.5
    
    # Tier adjustments
    if client_tier == "premium":
        base_weeks *= 1.3  # More complex features
    elif client_tier == "starter":
        base_weeks *= 0.8  # Simpler implementations
    
    # Convert to readable format
    if base_weeks <= 2:
        return "1-2 weeks"
    elif base_weeks <= 4:
        return "2-4 weeks"
    elif base_weeks <= 8:
        return "1-2 months"
    elif base_weeks <= 16:
        return "2-4 months"
    else:
        return "4+ months"
