"""
Deterministic timeline generation tool.

This tool generates project timelines and schedules
from task breakdowns using template-based planning.
"""

import logging
from datetime import datetime, timedelta
from typing import Any

logger = logging.getLogger(__name__)

# Timeline templates by project size
TIMELINE_TEMPLATES = {
    "small": {
        "total_weeks": 4,
        "phases": {
            "planning": {"weeks": 0.5, "percentage": 12},
            "setup": {"weeks": 0.5, "percentage": 12},
            "development": {"weeks": 2.5, "percentage": 63},
            "testing": {"weeks": 0.3, "percentage": 8},
            "deployment": {"weeks": 0.2, "percentage": 5},
        },
    },
    "medium": {
        "total_weeks": 8,
        "phases": {
            "planning": {"weeks": 1, "percentage": 12},
            "setup": {"weeks": 0.5, "percentage": 6},
            "development": {"weeks": 5, "percentage": 63},
            "testing": {"weeks": 1, "percentage": 12},
            "deployment": {"weeks": 0.5, "percentage": 7},
        },
    },
    "large": {
        "total_weeks": 16,
        "phases": {
            "planning": {"weeks": 2, "percentage": 12},
            "setup": {"weeks": 1, "percentage": 6},
            "development": {"weeks": 10, "percentage": 63},
            "testing": {"weeks": 2, "percentage": 12},
            "deployment": {"weeks": 1, "percentage": 7},
        },
    },
}

# Milestone templates
MILESTONE_TEMPLATES = {
    "setup_complete": {
        "name": "Setup Complete",
        "description": "Development environment and project structure ready",
        "deliverables": ["Project repository", "Development environment", "CI/CD pipeline"],
    },
    "mvp_ready": {
        "name": "MVP Ready",
        "description": "Minimum viable product with core features",
        "deliverables": ["Core functionality", "Basic UI", "Essential APIs"],
    },
    "feature_complete": {
        "name": "Feature Complete",
        "description": "All planned features implemented",
        "deliverables": ["Complete feature set", "Full UI", "All APIs"],
    },
    "testing_complete": {
        "name": "Testing Complete",
        "description": "All testing phases completed",
        "deliverables": ["Unit tests", "Integration tests", "User acceptance tests"],
    },
    "production_ready": {
        "name": "Production Ready",
        "description": "Application ready for production deployment",
        "deliverables": ["Production build", "Deployment setup", "Documentation"],
    },
}

# Risk factors that affect timeline
RISK_FACTORS = {
    "team_experience": {
        "junior": 1.3,    # 30% longer
        "mixed": 1.1,     # 10% longer
        "senior": 1.0,    # No adjustment
    },
    "project_complexity": {
        "simple": 0.9,    # 10% faster
        "moderate": 1.0,  # No adjustment
        "complex": 1.2,   # 20% longer
    },
    "business_type": {
        "general": 1.0,
        "ecommerce": 1.1,
        "healthcare": 1.3,
        "fintech": 1.4,
        "education": 1.1,
    },
}


def get_tool_metadata() -> dict[str, Any]:
    """Get metadata for the timeline generation tool."""
    return {
        "name": "generate_timeline",
        "description": "Generate project timeline and schedule from task breakdown",
        "version": "1.0.0",
        "category": "generation",
        "parameters": {
            "type": "object",
            "properties": {
                "tasks": {
                    "type": "object",
                    "description": "Task breakdown from generate_tasks tool",
                },
                "business_context": {
                    "type": "object",
                    "description": "Business type and project context",
                    "default": {},
                },
                "team_context": {
                    "type": "object",
                    "description": "Team size and experience information",
                    "default": {},
                },
                "start_date": {
                    "type": "string",
                    "description": "Project start date (YYYY-MM-DD)",
                    "default": None,
                },
                "timeline_style": {
                    "type": "string",
                    "enum": ["aggressive", "balanced", "conservative"],
                    "description": "Timeline approach",
                    "default": "balanced",
                },
            },
            "required": ["tasks"],
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "timeline_overview": {
                    "type": "object",
                    "description": "High-level timeline summary",
                },
                "phase_breakdown": {
                    "type": "array",
                    "description": "Detailed breakdown by project phases",
                },
                "milestones": {
                    "type": "array",
                    "description": "Key project milestones with dates",
                },
                "weekly_schedule": {
                    "type": "array",
                    "description": "Week-by-week task schedule",
                },
                "risk_assessment": {
                    "type": "object",
                    "description": "Timeline risks and contingency planning",
                },
            },
        },
        "dependencies": ["generate_tasks"],
    }


def run(parameters: dict[str, Any]) -> dict[str, Any]:
    """
    Generate project timeline from task breakdown.
    
    Args:
        parameters: Tool execution parameters
        
    Returns:
        Dictionary containing timeline and scheduling information
    """
    tasks = parameters.get("tasks", {})
    business_context = parameters.get("business_context", {})
    team_context = parameters.get("team_context", {})
    start_date_str = parameters.get("start_date")
    timeline_style = parameters.get("timeline_style", "balanced")
    
    if not tasks:
        return {
            "error": "Task breakdown must be provided for timeline generation",
            "timeline_overview": {},
            "phase_breakdown": [],
            "milestones": [],
            "weekly_schedule": [],
            "risk_assessment": {},
        }
    
    # Parse start date or use current date
    if start_date_str:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        except ValueError:
            start_date = datetime.now()
    else:
        start_date = datetime.now()
    
    logger.info("Generating %s timeline starting %s", timeline_style, start_date.strftime("%Y-%m-%d"))
    
    business_type = business_context.get("business_type", "general")
    team_size = team_context.get("team_size", 1)
    team_experience = team_context.get("experience_level", "mixed")
    
    # Determine project size and complexity
    project_size = _determine_project_size(tasks)
    complexity = _assess_project_complexity(tasks, business_type)
    
    # Generate timeline components
    timeline_overview = _create_timeline_overview(
        tasks, project_size, timeline_style, business_type, team_context,
    )
    
    phase_breakdown = _generate_phase_breakdown(
        tasks, project_size, timeline_style, start_date,
    )
    
    milestones = _generate_milestones(
        phase_breakdown, start_date, project_size,
    )
    
    weekly_schedule = _generate_weekly_schedule(
        tasks, phase_breakdown, start_date,
    )
    
    risk_assessment = _assess_timeline_risks(
        timeline_overview, business_type, team_experience, complexity,
    )
    
    return {
        "timeline_overview": timeline_overview,
        "phase_breakdown": phase_breakdown,
        "milestones": milestones,
        "weekly_schedule": weekly_schedule,
        "risk_assessment": risk_assessment,
        "generation_metadata": {
            "tool": "generate_timeline",
            "version": "1.0.0",
            "project_size": project_size,
            "timeline_style": timeline_style,
            "start_date": start_date.strftime("%Y-%m-%d"),
        },
    }


def _determine_project_size(tasks: dict[str, Any]) -> str:
    """Determine project size based on task complexity."""
    task_breakdown = tasks.get("task_breakdown", [])
    total_hours = tasks.get("effort_estimation", {}).get("total_hours", 0)
    task_count = len(task_breakdown)
    
    if total_hours < 100 or task_count < 15:
        return "small"
    elif total_hours < 400 or task_count < 40:
        return "medium"
    else:
        return "large"


def _assess_project_complexity(tasks: dict[str, Any], business_type: str) -> str:
    """Assess project complexity based on features and business type."""
    task_breakdown = tasks.get("task_breakdown", [])
    
    # Count complex features
    auth_tasks = sum(1 for task in task_breakdown if "auth" in task.get("name", "").lower())
    api_tasks = sum(1 for task in task_breakdown if "api" in task.get("name", "").lower())
    integration_tasks = sum(1 for task in task_breakdown if "integration" in task.get("name", "").lower())
    
    complexity_score = auth_tasks + api_tasks + integration_tasks
    
    # Adjust for business type
    if business_type in ["healthcare", "fintech"]:
        complexity_score += 2
    elif business_type in ["ecommerce"]:
        complexity_score += 1
    
    if complexity_score <= 3:
        return "simple"
    elif complexity_score <= 6:
        return "moderate"
    else:
        return "complex"


def _create_timeline_overview(
    tasks: dict[str, Any],
    project_size: str,
    timeline_style: str,
    business_type: str,
    team_context: dict[str, Any],
) -> dict[str, Any]:
    """Create high-level timeline overview."""
    base_template = TIMELINE_TEMPLATES[project_size]
    base_weeks = base_template["total_weeks"]
    
    # Apply timeline style adjustments
    style_multipliers = {
        "aggressive": 0.8,
        "balanced": 1.0,
        "conservative": 1.3,
    }
    
    # Apply risk factor adjustments
    team_experience = team_context.get("experience_level", "mixed")
    team_size = team_context.get("team_size", 1)
    
    risk_multiplier = (
        RISK_FACTORS["team_experience"].get(team_experience, 1.0) *
        RISK_FACTORS["business_type"].get(business_type, 1.0)
    )
    
    # Team size adjustment (diminishing returns)
    if team_size > 1:
        team_efficiency = min(team_size * 0.8, 3.0)  # Cap efficiency gain
    else:
        team_efficiency = 1.0
    
    # Calculate adjusted timeline
    adjusted_weeks = (
        base_weeks *
        style_multipliers[timeline_style] *
        risk_multiplier /
        team_efficiency
    )
    
    return {
        "total_weeks": round(adjusted_weeks, 1),
        "total_days": round(adjusted_weeks * 5),  # 5 working days per week
        "project_size": project_size,
        "timeline_style": timeline_style,
        "risk_multiplier": round(risk_multiplier, 2),
        "team_efficiency": round(team_efficiency, 2),
        "estimated_completion": "TBD",  # Will be set with actual dates
    }


def _generate_phase_breakdown(
    tasks: dict[str, Any],
    project_size: str,
    timeline_style: str,
    start_date: datetime,
) -> list[dict[str, Any]]:
    """Generate detailed phase breakdown with dates."""
    base_template = TIMELINE_TEMPLATES[project_size]
    phases = []
    current_date = start_date
    
    # Apply timeline style to phase durations
    style_adjustments = {
        "aggressive": {"development": 0.9, "testing": 0.7},
        "balanced": {},
        "conservative": {"development": 1.1, "testing": 1.3},
    }
    
    for phase_name, phase_info in base_template["phases"].items():
        base_weeks = phase_info["weeks"]
        
        # Apply style adjustments
        adjustment = style_adjustments.get(timeline_style, {}).get(phase_name, 1.0)
        adjusted_weeks = base_weeks * adjustment
        
        # Calculate dates
        phase_days = int(adjusted_weeks * 5)  # 5 working days per week
        end_date = current_date + timedelta(days=phase_days)
        
        phases.append({
            "name": phase_name.title(),
            "start_date": current_date.strftime("%Y-%m-%d"),
            "end_date": end_date.strftime("%Y-%m-%d"),
            "duration_weeks": round(adjusted_weeks, 1),
            "duration_days": phase_days,
            "percentage": phase_info["percentage"],
            "description": _get_phase_description(phase_name),
        })
        
        current_date = end_date + timedelta(days=1)  # Next phase starts next day
    
    return phases


def _generate_milestones(
    phases: list[dict[str, Any]],
    start_date: datetime,
    project_size: str,
) -> list[dict[str, Any]]:
    """Generate project milestones with dates."""
    milestones = []
    
    # Map phases to milestones
    milestone_mapping = {
        "Setup": "setup_complete",
        "Development": "mvp_ready" if project_size == "small" else "feature_complete",
        "Testing": "testing_complete",
        "Deployment": "production_ready",
    }
    
    for phase in phases:
        phase_name = phase["name"]
        
        if phase_name in milestone_mapping:
            milestone_key = milestone_mapping[phase_name]
            milestone_template = MILESTONE_TEMPLATES.get(milestone_key, {})
            
            milestones.append({
                "name": milestone_template.get("name", f"{phase_name} Complete"),
                "date": phase["end_date"],
                "description": milestone_template.get("description", f"{phase_name} phase completed"),
                "deliverables": milestone_template.get("deliverables", []),
                "phase": phase_name,
            })
    
    # Add MVP milestone for larger projects
    if project_size in ["medium", "large"]:
        dev_phase = next((p for p in phases if p["name"] == "Development"), None)
        if dev_phase:
            dev_start = datetime.strptime(dev_phase["start_date"], "%Y-%m-%d")
            dev_duration = dev_phase["duration_days"]
            mvp_date = dev_start + timedelta(days=int(dev_duration * 0.6))  # 60% through dev
            
            milestones.insert(-2, {  # Insert before testing milestone
                "name": "MVP Ready",
                "date": mvp_date.strftime("%Y-%m-%d"),
                "description": "Minimum viable product with core features",
                "deliverables": ["Core functionality", "Basic UI", "Essential APIs"],
                "phase": "Development",
            })
    
    return milestones


def _generate_weekly_schedule(
    tasks: dict[str, Any],
    phases: list[dict[str, Any]],
    start_date: datetime,
) -> list[dict[str, Any]]:
    """Generate week-by-week schedule."""
    weekly_schedule = []
    task_breakdown = tasks.get("task_breakdown", [])
    
    # Group tasks by category/phase
    task_groups = {}
    for task in task_breakdown:
        category = task.get("category", "other")
        if category not in task_groups:
            task_groups[category] = []
        task_groups[category].append(task)
    
    # Map categories to phases
    category_phase_mapping = {
        "setup": "Setup",
        "frontend": "Development",
        "backend": "Development", 
        "testing": "Testing",
        "deployment": "Deployment",
    }
    
    week_counter = 1
    current_date = start_date
    
    for phase in phases:
        phase_name = phase["name"]
        phase_start = datetime.strptime(phase["start_date"], "%Y-%m-%d")
        phase_end = datetime.strptime(phase["end_date"], "%Y-%m-%d")
        phase_weeks = phase["duration_weeks"]
        
        # Get tasks for this phase
        phase_categories = [cat for cat, mapped_phase in category_phase_mapping.items() if mapped_phase == phase_name]
        phase_tasks = []
        for category in phase_categories:
            phase_tasks.extend(task_groups.get(category, []))
        
        # Distribute tasks across weeks in this phase
        weeks_in_phase = max(1, int(phase_weeks))
        tasks_per_week = len(phase_tasks) // weeks_in_phase if phase_tasks else 0
        
        for week in range(weeks_in_phase):
            week_start = phase_start + timedelta(weeks=week)
            week_end = min(week_start + timedelta(days=6), phase_end)
            
            # Get tasks for this week
            start_idx = week * tasks_per_week
            end_idx = start_idx + tasks_per_week if week < weeks_in_phase - 1 else len(phase_tasks)
            week_tasks = phase_tasks[start_idx:end_idx]
            
            weekly_schedule.append({
                "week_number": week_counter,
                "start_date": week_start.strftime("%Y-%m-%d"),
                "end_date": week_end.strftime("%Y-%m-%d"),
                "phase": phase_name,
                "tasks": [task.get("name", "") for task in week_tasks],
                "estimated_hours": sum(task.get("estimated_hours", 0) for task in week_tasks),
                "focus_areas": list(set(task.get("category", "") for task in week_tasks)),
            })
            
            week_counter += 1
    
    return weekly_schedule


def _assess_timeline_risks(
    timeline_overview: dict[str, Any],
    business_type: str,
    team_experience: str,
    complexity: str,
) -> dict[str, Any]:
    """Assess timeline risks and create contingency plans."""
    risk_level = "low"
    risk_factors = []
    
    # Assess various risk factors
    if team_experience == "junior":
        risk_factors.append("Inexperienced team may require additional learning time")
        risk_level = "medium"
    
    if complexity == "complex":
        risk_factors.append("Complex project features may require additional development time")
        risk_level = "high" if risk_level != "high" else "high"
    
    if business_type in ["healthcare", "fintech"]:
        risk_factors.append(f"Strict {business_type} regulations may require additional compliance work")
        risk_level = "high"
    
    # Calculate buffer recommendations
    buffer_percentage = {
        "low": 10,
        "medium": 20, 
        "high": 30,
    }.get(risk_level, 20)
    
    total_weeks = timeline_overview.get("total_weeks", 0)
    buffer_weeks = total_weeks * (buffer_percentage / 100)
    
    return {
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "recommended_buffer": {
            "percentage": buffer_percentage,
            "weeks": round(buffer_weeks, 1),
        },
        "contingency_plans": _generate_contingency_plans(risk_level),
        "monitoring_points": _generate_monitoring_points(),
    }


def _get_phase_description(phase_name: str) -> str:
    """Get description for a project phase."""
    descriptions = {
        "planning": "Project planning, requirements analysis, and architecture design",
        "setup": "Environment setup, project initialization, and tooling configuration", 
        "development": "Core feature development and implementation",
        "testing": "Testing, quality assurance, and bug fixing",
        "deployment": "Production deployment and launch preparation",
    }
    return descriptions.get(phase_name, f"{phase_name.title()} phase activities")


def _generate_contingency_plans(risk_level: str) -> list[str]:
    """Generate contingency plans based on risk level."""
    base_plans = [
        "Add additional developer if timeline falls behind",
        "Reduce scope by deferring non-critical features",
        "Increase daily standup frequency for better tracking",
    ]
    
    if risk_level in ["medium", "high"]:
        base_plans.extend([
            "Schedule regular code reviews to catch issues early",
            "Implement feature flags for safer deployments",
        ])
    
    if risk_level == "high":
        base_plans.extend([
            "Engage external consultants for specialized expertise",
            "Consider phased deployment to reduce risk",
        ])
    
    return base_plans


def _generate_monitoring_points() -> list[str]:
    """Generate timeline monitoring checkpoints."""
    return [
        "Weekly progress reviews with stakeholders",
        "End of each phase milestone assessment",
        "Monthly budget and timeline review",
        "Critical dependency tracking",
        "Quality metrics monitoring",
    ]
