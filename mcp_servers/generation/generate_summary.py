"""
Deterministic summary generation tool.

This tool generates comprehensive project summaries
from all analysis and planning outputs using template-based consolidation.
"""

import logging
from typing import Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Summary templates by section
SUMMARY_TEMPLATES = {
    "executive": {
        "title": "Executive Summary",
        "sections": [
            "Project Overview",
            "Key Objectives", 
            "Timeline & Budget",
            "Success Metrics",
            "Risk Assessment",
        ],
    },
    "technical": {
        "title": "Technical Summary", 
        "sections": [
            "Architecture Overview",
            "Technology Stack",
            "Key Components",
            "Integration Points",
            "Security Considerations",
        ],
    },
    "project": {
        "title": "Project Plan Summary",
        "sections": [
            "Phase Breakdown",
            "Resource Requirements",
            "Dependencies & Risks",
            "Quality Assurance",
            "Deployment Strategy",
        ],
    },
}

# Key metrics to track
KEY_METRICS = {
    "scope": [
        "Total features",
        "Pages/screens", 
        "API endpoints",
        "Database tables",
        "Components",
    ],
    "effort": [
        "Total estimated hours",
        "Development weeks",
        "Team size required",
        "Cost estimate",
    ],
    "quality": [
        "Test coverage target",
        "Performance benchmarks", 
        "Security compliance",
        "Accessibility standards",
    ],
}


def get_tool_metadata() -> dict[str, Any]:
    """Get metadata for the summary generation tool."""
    return {
        "name": "generate_summary",
        "description": "Generate comprehensive project summary from all analysis outputs",
        "version": "1.0.0",
        "category": "generation", 
        "parameters": {
            "type": "object",
            "properties": {
                "requirements": {
                    "type": "object",
                    "description": "Requirements analysis results",
                },
                "assets": {
                    "type": "object",
                    "description": "Project assets from extract_assets tool",
                },
                "tasks": {
                    "type": "object",
                    "description": "Task breakdown from generate_tasks tool",
                },
                "timeline": {
                    "type": "object", 
                    "description": "Timeline from generate_timeline tool",
                },
                "gaps_analysis": {
                    "type": "object",
                    "description": "Gap analysis from detect_missing tool",
                    "default": {},
                },
                "business_context": {
                    "type": "object",
                    "description": "Business type and project context",
                    "default": {},
                },
                "summary_style": {
                    "type": "string",
                    "enum": ["executive", "technical", "comprehensive"],
                    "description": "Style and depth of summary",
                    "default": "comprehensive",
                },
            },
            "required": ["requirements", "assets", "tasks", "timeline"],
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "executive_summary": {
                    "type": "object",
                    "description": "High-level executive summary",
                },
                "technical_summary": {
                    "type": "object", 
                    "description": "Technical implementation summary",
                },
                "project_summary": {
                    "type": "object",
                    "description": "Project planning and execution summary",
                },
                "key_metrics": {
                    "type": "object",
                    "description": "Consolidated project metrics",
                },
                "recommendations": {
                    "type": "array",
                    "description": "Key recommendations and next steps",
                },
            },
        },
        "dependencies": ["extract_requirements", "extract_assets", "generate_tasks", "generate_timeline"],
    }


def run(parameters: dict[str, Any]) -> dict[str, Any]:
    """
    Generate comprehensive project summary.
    
    Args:
        parameters: Tool execution parameters
        
    Returns:
        Dictionary containing project summary and recommendations
    """
    requirements = parameters.get("requirements", {})
    assets = parameters.get("assets", {})
    tasks = parameters.get("tasks", {})
    timeline = parameters.get("timeline", {})
    gaps_analysis = parameters.get("gaps_analysis", {})
    business_context = parameters.get("business_context", {})
    summary_style = parameters.get("summary_style", "comprehensive")
    
    if not all([requirements, assets, tasks, timeline]):
        return {
            "error": "Requirements, assets, tasks, and timeline must be provided for summary generation",
            "executive_summary": {},
            "technical_summary": {},
            "project_summary": {},
            "key_metrics": {},
            "recommendations": [],
        }
    
    logger.info("Generating %s project summary", summary_style)
    
    business_type = business_context.get("business_type", "general")
    
    # Generate different summary sections
    executive_summary = _generate_executive_summary(
        requirements, assets, tasks, timeline, business_type,
    )
    
    technical_summary = _generate_technical_summary(
        requirements, assets, tasks, business_type,
    )
    
    project_summary = _generate_project_summary(
        tasks, timeline, gaps_analysis,
    )
    
    key_metrics = _consolidate_key_metrics(
        requirements, assets, tasks, timeline,
    )
    
    recommendations = _generate_recommendations(
        gaps_analysis, timeline, business_type, summary_style,
    )
    
    return {
        "executive_summary": executive_summary,
        "technical_summary": technical_summary,
        "project_summary": project_summary,
        "key_metrics": key_metrics,
        "recommendations": recommendations,
        "generation_metadata": {
            "tool": "generate_summary",
            "version": "1.0.0",
            "summary_style": summary_style,
            "generated_at": datetime.now().isoformat(),
        },
    }


def _generate_executive_summary(
    requirements: dict[str, Any],
    assets: dict[str, Any],
    tasks: dict[str, Any],
    timeline: dict[str, Any],
    business_type: str,
) -> dict[str, Any]:
    """Generate executive-level project summary."""
    
    # Extract key project information
    functional_reqs = requirements.get("functional_requirements", [])
    asset_summary = assets.get("asset_summary", {})
    effort_estimation = tasks.get("effort_estimation", {})
    timeline_overview = timeline.get("timeline_overview", {})
    
    # Project scope analysis
    total_features = len(functional_reqs)
    total_assets = asset_summary.get("total_count", 0)
    total_weeks = timeline_overview.get("total_weeks", 0)
    total_hours = effort_estimation.get("total_hours", 0)
    
    # Business value proposition
    value_drivers = _identify_value_drivers(functional_reqs, business_type)
    
    # Risk assessment
    risk_level = timeline.get("risk_assessment", {}).get("risk_level", "medium")
    
    return {
        "project_overview": {
            "business_type": business_type.title(),
            "scope_complexity": _assess_scope_complexity(total_features, total_assets),
            "primary_value_drivers": value_drivers,
            "target_users": _identify_target_users(functional_reqs, business_type),
        },
        "key_objectives": {
            "primary_goals": _extract_primary_goals(functional_reqs),
            "success_criteria": _define_success_criteria(functional_reqs, business_type),
            "business_impact": _assess_business_impact(functional_reqs, business_type),
        },
        "timeline_budget": {
            "duration_weeks": total_weeks,
            "estimated_hours": total_hours,
            "resource_requirements": effort_estimation.get("team_size", 1),
            "cost_estimate_range": _estimate_cost_range(total_hours),
        },
        "success_metrics": {
            "delivery_timeline": f"{total_weeks} weeks",
            "feature_completion": "100% of core features",
            "quality_targets": "90% test coverage, < 2s page load",
            "user_satisfaction": "4.0+ app store rating target",
        },
        "risk_assessment": {
            "overall_risk": risk_level,
            "primary_risks": timeline.get("risk_assessment", {}).get("risk_factors", [])[:3],
            "mitigation_strategy": "Phased delivery with regular checkpoints",
        },
    }


def _generate_technical_summary(
    requirements: dict[str, Any],
    assets: dict[str, Any],
    tasks: dict[str, Any],
    business_type: str,
) -> dict[str, Any]:
    """Generate technical implementation summary."""
    
    frontend_assets = assets.get("frontend_assets", [])
    backend_assets = assets.get("backend_assets", [])
    task_breakdown = tasks.get("task_breakdown", [])
    
    # Technology stack analysis
    tech_stack = _determine_tech_stack(requirements, business_type)
    
    # Architecture complexity
    architecture_complexity = _assess_architecture_complexity(frontend_assets, backend_assets)
    
    # Integration requirements
    integrations = _identify_integrations(backend_assets, business_type)
    
    return {
        "architecture_overview": {
            "application_type": _determine_app_type(frontend_assets, backend_assets),
            "complexity_level": architecture_complexity,
            "scalability_requirements": _assess_scalability_needs(requirements),
            "performance_requirements": _assess_performance_needs(requirements),
        },
        "technology_stack": {
            "frontend": tech_stack["frontend"],
            "backend": tech_stack["backend"],
            "database": tech_stack["database"],
            "deployment": tech_stack["deployment"],
        },
        "key_components": {
            "frontend_components": len([a for a in frontend_assets if a.get("category") == "component"]),
            "api_endpoints": len([a for a in backend_assets if a.get("category") == "api"]),
            "database_tables": len([a for a in backend_assets if a.get("category") == "database"]),
            "third_party_services": len(integrations),
        },
        "integration_points": {
            "external_apis": integrations,
            "authentication_system": "JWT-based" if _has_auth_requirement(requirements) else "None",
            "payment_processing": "Required" if business_type == "ecommerce" else "Not required",
        },
        "security_considerations": {
            "authentication_required": _has_auth_requirement(requirements),
            "data_encryption": "Required" if business_type in ["healthcare", "fintech"] else "Standard",
            "compliance_requirements": _get_compliance_requirements(business_type),
            "security_testing": "Penetration testing recommended" if business_type in ["fintech", "healthcare"] else "Standard testing",
        },
    }


def _generate_project_summary(
    tasks: dict[str, Any],
    timeline: dict[str, Any],
    gaps_analysis: dict[str, Any],
) -> dict[str, Any]:
    """Generate project planning and execution summary."""
    
    task_summary = tasks.get("task_summary", {})
    phases = timeline.get("phase_breakdown", [])
    milestones = timeline.get("milestones", [])
    risk_assessment = timeline.get("risk_assessment", {})
    
    return {
        "phase_breakdown": {
            "total_phases": len(phases),
            "development_phase_weeks": next(
                (p["duration_weeks"] for p in phases if p["name"] == "Development"), 0,
            ),
            "testing_phase_weeks": next(
                (p["duration_weeks"] for p in phases if p["name"] == "Testing"), 0,
            ),
            "key_milestones": len(milestones),
        },
        "resource_requirements": {
            "total_tasks": task_summary.get("total_tasks", 0),
            "development_tasks": task_summary.get("by_category", {}).get("frontend", 0) + 
                             task_summary.get("by_category", {}).get("backend", 0),
            "testing_tasks": task_summary.get("by_category", {}).get("testing", 0),
            "estimated_team_size": tasks.get("effort_estimation", {}).get("team_size", 1),
        },
        "dependencies_risks": {
            "critical_dependencies": _identify_critical_dependencies(tasks),
            "risk_level": risk_assessment.get("risk_level", "medium"),
            "buffer_recommended": risk_assessment.get("recommended_buffer", {}).get("weeks", 0),
            "identified_gaps": gaps_analysis.get("gap_summary", {}).get("total_gaps", 0),
        },
        "quality_assurance": {
            "testing_strategy": "Unit + Integration + E2E testing",
            "code_review_process": "Required for all changes",
            "deployment_strategy": "Staged deployment with rollback capability",
            "monitoring_plan": "Application performance and error monitoring",
        },
        "deployment_strategy": {
            "environment_setup": "Development → Staging → Production",
            "deployment_method": "Automated CI/CD pipeline",
            "rollback_strategy": "Automated rollback on failure detection",
            "monitoring_alerts": "Real-time error and performance monitoring",
        },
    }


def _consolidate_key_metrics(
    requirements: dict[str, Any],
    assets: dict[str, Any],
    tasks: dict[str, Any],
    timeline: dict[str, Any],
) -> dict[str, Any]:
    """Consolidate key project metrics."""
    
    functional_reqs = requirements.get("functional_requirements", [])
    asset_summary = assets.get("asset_summary", {})
    task_summary = tasks.get("task_summary", {})
    effort_estimation = tasks.get("effort_estimation", {})
    timeline_overview = timeline.get("timeline_overview", {})
    
    return {
        "scope_metrics": {
            "total_features": len(functional_reqs),
            "pages_screens": len([a for a in assets.get("frontend_assets", []) if "page" in a.get("category", "")]),
            "api_endpoints": len([a for a in assets.get("backend_assets", []) if a.get("category") == "api"]),
            "database_tables": len([a for a in assets.get("backend_assets", []) if a.get("category") == "database"]),
            "components": len([a for a in assets.get("frontend_assets", []) if a.get("category") == "component"]),
        },
        "effort_metrics": {
            "total_estimated_hours": effort_estimation.get("total_hours", 0),
            "development_weeks": timeline_overview.get("total_weeks", 0),
            "team_size_required": effort_estimation.get("team_size", 1),
            "cost_estimate": _estimate_cost_range(effort_estimation.get("total_hours", 0)),
        },
        "quality_metrics": {
            "test_coverage_target": "90%",
            "performance_benchmarks": "< 2s page load, < 500ms API response",
            "security_compliance": _get_compliance_requirements(assets.get("business_type", "general")),
            "accessibility_standards": "WCAG 2.1 AA compliance",
        },
    }


def _generate_recommendations(
    gaps_analysis: dict[str, Any],
    timeline: dict[str, Any],
    business_type: str,
    summary_style: str,
) -> list[dict[str, Any]]:
    """Generate key recommendations and next steps."""
    
    recommendations = []
    
    # Timeline recommendations
    risk_level = timeline.get("risk_assessment", {}).get("risk_level", "medium")
    if risk_level in ["medium", "high"]:
        recommendations.append({
            "category": "timeline",
            "priority": "high",
            "title": "Add Timeline Buffer",
            "description": f"Add {timeline.get('risk_assessment', {}).get('recommended_buffer', {}).get('weeks', 2)} week buffer for {risk_level} risk project",
            "impact": "Reduces delivery risk and improves quality",
        })
    
    # Gap analysis recommendations
    critical_gaps = len(gaps_analysis.get("critical_gaps", []))
    if critical_gaps > 0:
        recommendations.append({
            "category": "scope",
            "priority": "critical",
            "title": "Address Critical Gaps", 
            "description": f"Resolve {critical_gaps} critical missing components before development",
            "impact": "Prevents project blocking issues",
        })
    
    # Business-specific recommendations
    if business_type == "ecommerce":
        recommendations.append({
            "category": "business",
            "priority": "high",
            "title": "Payment Security Focus",
            "description": "Implement PCI DSS compliance for payment processing",
            "impact": "Ensures regulatory compliance and customer trust",
        })
    elif business_type in ["healthcare", "fintech"]:
        recommendations.append({
            "category": "compliance",
            "priority": "critical", 
            "title": "Regulatory Compliance Review",
            "description": f"Conduct thorough {business_type} compliance review with legal team",
            "impact": "Prevents regulatory violations and legal issues",
        })
    
    # Technical recommendations
    if summary_style == "comprehensive":
        recommendations.extend([
            {
                "category": "technical",
                "priority": "medium",
                "title": "Architecture Review",
                "description": "Conduct technical architecture review with senior developers",
                "impact": "Validates technical approach and identifies improvements",
            },
            {
                "category": "quality",
                "priority": "medium", 
                "title": "Testing Strategy",
                "description": "Implement comprehensive testing strategy from project start",
                "impact": "Reduces bugs and improves long-term maintainability",
            },
        ])
    
    # Process recommendations
    recommendations.append({
        "category": "process",
        "priority": "medium",
        "title": "Regular Stakeholder Reviews",
        "description": "Schedule weekly progress reviews with key stakeholders",
        "impact": "Ensures alignment and early issue detection",
    })
    
    return recommendations


# Helper functions for summary generation

def _assess_scope_complexity(features: int, assets: int) -> str:
    """Assess overall scope complexity."""
    total_complexity = features + assets
    if total_complexity < 20:
        return "Simple"
    elif total_complexity < 50:
        return "Moderate"
    else:
        return "Complex"


def _identify_value_drivers(functional_reqs: list[dict[str, Any]], business_type: str) -> list[str]:
    """Identify key business value drivers."""
    drivers = ["Improved user experience", "Operational efficiency"]
    
    if any("auth" in req.get("category", "").lower() for req in functional_reqs):
        drivers.append("User engagement and retention")
    
    if business_type == "ecommerce":
        drivers.extend(["Increased sales conversion", "Customer data insights"])
    elif business_type == "healthcare":
        drivers.extend(["Patient care quality", "Regulatory compliance"])
    elif business_type == "fintech":
        drivers.extend(["Financial service efficiency", "Risk management"])
    
    return drivers[:4]  # Return top 4 drivers


def _identify_target_users(functional_reqs: list[dict[str, Any]], business_type: str) -> str:
    """Identify primary target user groups."""
    has_admin = any("admin" in req.get("category", "").lower() for req in functional_reqs)
    
    if business_type == "healthcare":
        return "Patients, healthcare providers, and administrators"
    elif business_type == "ecommerce":
        return "Online shoppers and store administrators"
    elif business_type == "fintech":
        return "Financial service customers and compliance officers"
    elif has_admin:
        return "End users and system administrators"
    else:
        return "General application users"


def _extract_primary_goals(functional_reqs: list[dict[str, Any]]) -> list[str]:
    """Extract primary project goals."""
    goals = ["Deliver core functionality"]
    
    categories = [req.get("category", "") for req in functional_reqs]
    
    if "web" in categories:
        goals.append("Provide intuitive web interface")
    if "data" in categories:
        goals.append("Enable efficient data management") 
    if "auth" in categories:
        goals.append("Ensure secure user authentication")
    
    return goals[:3]  # Return top 3 goals


def _define_success_criteria(functional_reqs: list[dict[str, Any]], business_type: str) -> list[str]:
    """Define measurable success criteria."""
    criteria = [
        "100% core feature completion",
        "< 2 second page load times",
        "90%+ test coverage",
    ]
    
    if business_type == "ecommerce":
        criteria.append("< 3% cart abandonment increase")
    elif business_type in ["healthcare", "fintech"]:
        criteria.append("100% regulatory compliance")
    
    return criteria


def _assess_business_impact(functional_reqs: list[dict[str, Any]], business_type: str) -> str:
    """Assess expected business impact."""
    feature_count = len(functional_reqs)
    
    if business_type in ["healthcare", "fintech"]:
        return "High - regulatory compliance and operational efficiency"
    elif business_type == "ecommerce":
        return "High - direct revenue impact through improved conversion"
    elif feature_count > 10:
        return "Medium-High - significant operational improvements"
    else:
        return "Medium - operational efficiency and user satisfaction"


def _estimate_cost_range(total_hours: int) -> str:
    """Estimate cost range based on hours."""
    # Using average developer rate of $75-150/hour
    low_cost = total_hours * 75
    high_cost = total_hours * 150
    
    if low_cost < 10000:
        return f"${low_cost:,} - ${high_cost:,} (Small project)"
    elif low_cost < 50000:
        return f"${low_cost:,} - ${high_cost:,} (Medium project)"
    else:
        return f"${low_cost:,} - ${high_cost:,} (Large project)"


def _determine_tech_stack(requirements: dict[str, Any], business_type: str) -> dict[str, str]:
    """Determine appropriate technology stack."""
    has_auth = any("auth" in req.get("category", "").lower() 
                  for req in requirements.get("functional_requirements", []))
    
    return {
        "frontend": "React + TypeScript + Tailwind CSS",
        "backend": "Node.js + Express" if has_auth else "Static hosting",
        "database": "PostgreSQL" if has_auth else "Local storage",
        "deployment": "Vercel" if not has_auth else "Railway/Heroku",
    }


def _determine_app_type(frontend_assets: list[dict[str, Any]], backend_assets: list[dict[str, Any]]) -> str:
    """Determine application type."""
    has_pages = any(a.get("category") == "web_page" for a in frontend_assets)
    has_apis = any(a.get("category") == "api" for a in backend_assets)
    
    if has_pages and has_apis:
        return "Full-stack web application"
    elif has_pages:
        return "Frontend web application"
    else:
        return "API service"


def _assess_architecture_complexity(frontend_assets: list[dict[str, Any]], backend_assets: list[dict[str, Any]]) -> str:
    """Assess architecture complexity."""
    total_assets = len(frontend_assets) + len(backend_assets)
    
    if total_assets < 10:
        return "Simple"
    elif total_assets < 25:
        return "Moderate"
    else:
        return "Complex"


def _assess_scalability_needs(requirements: dict[str, Any]) -> str:
    """Assess scalability requirements."""
    functional_reqs = requirements.get("functional_requirements", [])
    
    if len(functional_reqs) > 15:
        return "High - anticipate significant user load"
    elif len(functional_reqs) > 8:
        return "Medium - moderate scalability requirements"
    else:
        return "Low - basic scalability needs"


def _assess_performance_needs(requirements: dict[str, Any]) -> str:
    """Assess performance requirements."""
    return "Standard web performance - < 2s page load, < 500ms API response"


def _identify_integrations(backend_assets: list[dict[str, Any]], business_type: str) -> list[str]:
    """Identify external integrations."""
    integrations = []
    
    if business_type == "ecommerce":
        integrations.extend(["Payment gateway", "Inventory management", "Shipping APIs"])
    elif business_type == "healthcare":
        integrations.extend(["EMR systems", "Insurance verification", "Lab results"])
    elif business_type == "fintech":
        integrations.extend(["Banking APIs", "Credit scoring", "Regulatory reporting"])
    
    # Check for common integrations in assets
    for asset in backend_assets:
        name = asset.get("name", "").lower()
        if "email" in name:
            integrations.append("Email service")
        elif "payment" in name:
            integrations.append("Payment processing")
    
    return list(set(integrations))  # Remove duplicates


def _has_auth_requirement(requirements: dict[str, Any]) -> bool:
    """Check if authentication is required."""
    return any("auth" in req.get("category", "").lower() 
              for req in requirements.get("functional_requirements", []))


def _get_compliance_requirements(business_type: str) -> str:
    """Get compliance requirements by business type."""
    compliance_map = {
        "healthcare": "HIPAA compliance required",
        "fintech": "SOX, PCI DSS compliance required",
        "ecommerce": "PCI DSS for payments",
        "education": "FERPA compliance recommended",
        "general": "GDPR compliance recommended",
    }
    return compliance_map.get(business_type, "Standard security practices")


def _identify_critical_dependencies(tasks: dict[str, Any]) -> list[str]:
    """Identify critical project dependencies."""
    task_breakdown = tasks.get("task_breakdown", [])
    
    # Find tasks with high priority and multiple dependencies
    critical_deps = []
    for task in task_breakdown:
        if task.get("priority") == "high" and len(task.get("dependencies", [])) > 0:
            critical_deps.extend(task.get("dependencies", []))
    
    # Return most common dependencies
    from collections import Counter
    dep_counts = Counter(critical_deps)
    return [dep for dep, count in dep_counts.most_common(3)]
