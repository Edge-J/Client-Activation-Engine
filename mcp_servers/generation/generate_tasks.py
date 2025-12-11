"""
Deterministic task generation tool.

This tool generates detailed task breakdowns and work items
from project specifications using template-based planning.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# Task templates by category
TASK_TEMPLATES = {
    "setup": [
        {
            "name": "Project Initialization",
            "description": "Set up project structure and dependencies",
            "estimated_hours": 2,
            "category": "setup",
            "priority": "high",
            "dependencies": [],
            "subtasks": [
                "Create project repository",
                "Initialize package.json", 
                "Install core dependencies",
                "Set up development environment",
            ],
        },
        {
            "name": "Development Environment Setup",
            "description": "Configure development tools and workflows",
            "estimated_hours": 3,
            "category": "setup", 
            "priority": "high",
            "dependencies": ["Project Initialization"],
            "subtasks": [
                "Configure linting and formatting",
                "Set up build system",
                "Configure development server",
                "Set up testing framework",
            ],
        },
    ],
    "frontend": [
        {
            "name": "UI Component Development",
            "description": "Create reusable React components",
            "estimated_hours": 8,
            "category": "frontend",
            "priority": "high",
            "dependencies": ["Development Environment Setup"],
            "subtasks": [
                "Create base component structure",
                "Implement styling system",
                "Add component props and state",
                "Create component documentation",
            ],
        },
        {
            "name": "Page Implementation",
            "description": "Build application pages and routing",
            "estimated_hours": 12,
            "category": "frontend",
            "priority": "high", 
            "dependencies": ["UI Component Development"],
            "subtasks": [
                "Set up routing system",
                "Create page components",
                "Implement navigation",
                "Add responsive design",
            ],
        },
        {
            "name": "State Management",
            "description": "Implement application state management",
            "estimated_hours": 6,
            "category": "frontend",
            "priority": "medium",
            "dependencies": ["Page Implementation"],
            "subtasks": [
                "Set up state management library",
                "Create state schemas",
                "Implement actions and reducers",
                "Connect components to state",
            ],
        },
    ],
    "backend": [
        {
            "name": "API Development", 
            "description": "Create backend API endpoints",
            "estimated_hours": 10,
            "category": "backend",
            "priority": "high",
            "dependencies": ["Database Setup"],
            "subtasks": [
                "Set up API framework",
                "Create route handlers",
                "Implement request validation",
                "Add error handling",
            ],
        },
        {
            "name": "Database Setup",
            "description": "Set up database schema and connections",
            "estimated_hours": 6,
            "category": "backend",
            "priority": "high",
            "dependencies": ["Development Environment Setup"],
            "subtasks": [
                "Design database schema",
                "Set up database connection",
                "Create migration scripts",
                "Seed initial data",
            ],
        },
        {
            "name": "Authentication System",
            "description": "Implement user authentication and authorization",
            "estimated_hours": 8,
            "category": "backend",
            "priority": "high",
            "dependencies": ["API Development"],
            "subtasks": [
                "Set up authentication middleware",
                "Create login/logout endpoints",
                "Implement JWT token system", 
                "Add password hashing",
            ],
        },
    ],
    "testing": [
        {
            "name": "Unit Testing",
            "description": "Write unit tests for components and functions",
            "estimated_hours": 8,
            "category": "testing",
            "priority": "medium",
            "dependencies": ["UI Component Development", "API Development"],
            "subtasks": [
                "Set up testing framework",
                "Write component tests",
                "Write API endpoint tests",
                "Create test utilities",
            ],
        },
        {
            "name": "Integration Testing",
            "description": "Test application workflow and integration points",
            "estimated_hours": 6,
            "category": "testing", 
            "priority": "medium",
            "dependencies": ["Unit Testing"],
            "subtasks": [
                "Set up integration test environment",
                "Write user flow tests",
                "Test API integrations",
                "Add performance tests",
            ],
        },
    ],
    "deployment": [
        {
            "name": "Production Setup",
            "description": "Prepare application for production deployment",
            "estimated_hours": 4,
            "category": "deployment",
            "priority": "high",
            "dependencies": ["Integration Testing"],
            "subtasks": [
                "Configure production build",
                "Set up environment variables",
                "Configure deployment platform",
                "Set up monitoring",
            ],
        },
        {
            "name": "Documentation",
            "description": "Create project documentation",
            "estimated_hours": 4,
            "category": "deployment",
            "priority": "medium",
            "dependencies": ["Production Setup"],
            "subtasks": [
                "Write README documentation",
                "Create API documentation",
                "Document deployment process",
                "Create user guides",
            ],
        },
    ],
}

# Business-specific task adjustments
BUSINESS_SPECIFIC_TASKS = {
    "ecommerce": [
        {
            "name": "Shopping Cart Implementation",
            "description": "Implement shopping cart functionality",
            "estimated_hours": 6,
            "category": "frontend",
            "priority": "high",
        },
        {
            "name": "Payment Integration",
            "description": "Integrate payment processing system",
            "estimated_hours": 8,
            "category": "backend", 
            "priority": "high",
        },
    ],
    "healthcare": [
        {
            "name": "HIPAA Compliance Implementation",
            "description": "Ensure HIPAA compliance measures",
            "estimated_hours": 10,
            "category": "backend",
            "priority": "critical",
        },
    ],
    "fintech": [
        {
            "name": "Financial Compliance Setup",
            "description": "Implement financial regulations compliance",
            "estimated_hours": 12,
            "category": "backend",
            "priority": "critical",
        },
    ],
}


def get_tool_metadata() -> dict[str, Any]:
    """Get metadata for the task generation tool."""
    return {
        "name": "generate_tasks",
        "description": "Generate detailed task breakdown from project specifications",
        "version": "1.0.0",
        "category": "generation",
        "parameters": {
            "type": "object",
            "properties": {
                "specification": {
                    "type": "object",
                    "description": "Project specification (e.g., from generate_lovable_spec)",
                },
                "assets": {
                    "type": "object",
                    "description": "Project assets from extract_assets tool",
                },
                "business_context": {
                    "type": "object",
                    "description": "Business type and project context",
                    "default": {},
                },
                "team_size": {
                    "type": "integer",
                    "description": "Number of developers on the team",
                    "default": 1,
                },
                "timeline_preference": {
                    "type": "string",
                    "enum": ["fast", "balanced", "thorough"],
                    "description": "Timeline preference affecting task priorities",
                    "default": "balanced",
                },
            },
            "required": ["specification", "assets"],
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "task_breakdown": {
                    "type": "array",
                    "description": "Detailed task list with dependencies",
                },
                "task_summary": {
                    "type": "object",
                    "description": "Summary of tasks by category and priority",
                },
                "dependency_graph": {
                    "type": "object",
                    "description": "Task dependency relationships",
                },
                "effort_estimation": {
                    "type": "object",
                    "description": "Total effort estimates by category",
                },
            },
        },
        "dependencies": ["generate_lovable_spec", "extract_assets"],
    }


def run(parameters: dict[str, Any]) -> dict[str, Any]:
    """
    Generate detailed task breakdown from project specification.
    
    Args:
        parameters: Tool execution parameters
        
    Returns:
        Dictionary containing task breakdown and planning information
    """
    specification = parameters.get("specification", {})
    assets = parameters.get("assets", {})
    business_context = parameters.get("business_context", {})
    team_size = parameters.get("team_size", 1)
    timeline_preference = parameters.get("timeline_preference", "balanced")
    
    if not specification or not assets:
        return {
            "error": "Specification and assets must be provided for task generation",
            "task_breakdown": [],
            "task_summary": {},
            "dependency_graph": {},
            "effort_estimation": {},
        }
    
    logger.info("Generating tasks for %s timeline with team size %d", timeline_preference, team_size)
    
    business_type = business_context.get("business_type", "general")
    
    # Generate tasks based on project characteristics
    task_breakdown = _generate_task_list(specification, assets, business_type, timeline_preference)
    task_summary = _create_task_summary(task_breakdown)
    dependency_graph = _build_dependency_graph(task_breakdown)
    effort_estimation = _calculate_effort_estimation(task_breakdown, team_size)
    
    return {
        "task_breakdown": task_breakdown,
        "task_summary": task_summary,
        "dependency_graph": dependency_graph,
        "effort_estimation": effort_estimation,
        "generation_metadata": {
            "tool": "generate_tasks",
            "version": "1.0.0",
            "business_type": business_type,
            "team_size": team_size,
            "timeline_preference": timeline_preference,
        },
    }


def _generate_task_list(
    specification: dict[str, Any], 
    assets: dict[str, Any], 
    business_type: str,
    timeline_preference: str,
) -> list[dict[str, Any]]:
    """Generate comprehensive task list based on project characteristics."""
    tasks = []
    
    # Always include setup tasks
    tasks.extend(_customize_tasks(TASK_TEMPLATES["setup"], timeline_preference))
    
    # Analyze specification to determine needed task categories
    spec_components = specification.get("component_list", [])
    spec_pages = specification.get("page_structure", {}).get("pages", [])
    spec_apis = specification.get("api_endpoints", [])
    
    # Frontend tasks
    if spec_components or spec_pages:
        frontend_tasks = _customize_tasks(TASK_TEMPLATES["frontend"], timeline_preference)
        tasks.extend(frontend_tasks)
    
    # Backend tasks
    if spec_apis or any("backend" in asset.get("category", "") for asset in assets.get("backend_assets", [])):
        backend_tasks = _customize_tasks(TASK_TEMPLATES["backend"], timeline_preference)
        tasks.extend(backend_tasks)
    
    # Testing tasks (reduced for fast timeline)
    if timeline_preference != "fast":
        testing_tasks = _customize_tasks(TASK_TEMPLATES["testing"], timeline_preference)
        tasks.extend(testing_tasks)
    
    # Deployment tasks
    deployment_tasks = _customize_tasks(TASK_TEMPLATES["deployment"], timeline_preference)
    tasks.extend(deployment_tasks)
    
    # Add business-specific tasks
    if business_type in BUSINESS_SPECIFIC_TASKS:
        business_tasks = _customize_tasks(
            BUSINESS_SPECIFIC_TASKS[business_type], 
            timeline_preference,
        )
        tasks.extend(business_tasks)
    
    # Add component-specific tasks
    component_tasks = _generate_component_tasks(spec_components, timeline_preference)
    tasks.extend(component_tasks)
    
    # Add page-specific tasks
    page_tasks = _generate_page_tasks(spec_pages, timeline_preference)
    tasks.extend(page_tasks)
    
    return tasks


def _customize_tasks(task_list: list[dict[str, Any]], timeline_preference: str) -> list[dict[str, Any]]:
    """Customize tasks based on timeline preference."""
    customized = []
    
    for task in task_list:
        customized_task = task.copy()
        
        # Adjust priority and effort based on timeline
        if timeline_preference == "fast":
            # Reduce non-critical tasks
            if customized_task.get("priority") == "medium":
                customized_task["priority"] = "low"
            # Reduce estimated hours for faster completion
            customized_task["estimated_hours"] = int(customized_task.get("estimated_hours", 0) * 0.8)
            
        elif timeline_preference == "thorough":
            # Increase thoroughness
            if customized_task.get("priority") == "medium":
                customized_task["priority"] = "high"
            # Add extra time for quality
            customized_task["estimated_hours"] = int(customized_task.get("estimated_hours", 0) * 1.2)
        
        customized.append(customized_task)
    
    return customized


def _generate_component_tasks(components: list[dict[str, Any]], timeline_preference: str) -> list[dict[str, Any]]:
    """Generate tasks for specific components."""
    tasks = []
    
    for component in components:
        component_name = component.get("name", "")
        
        task = {
            "name": f"Implement {component_name} Component",
            "description": f"Create and test {component_name} component",
            "estimated_hours": 3 if timeline_preference == "fast" else 4,
            "category": "frontend",
            "priority": "high" if component.get("type") == "essential" else "medium",
            "dependencies": ["UI Component Development"],
            "subtasks": [
                f"Create {component_name} component structure",
                f"Implement {component_name} functionality",
                f"Add {component_name} styling",
                f"Test {component_name} component",
            ],
        }
        
        tasks.append(task)
    
    return tasks


def _generate_page_tasks(pages: list[dict[str, Any]], timeline_preference: str) -> list[dict[str, Any]]:
    """Generate tasks for specific pages."""
    tasks = []
    
    for page in pages:
        page_name = page.get("name", "")
        
        # Determine priority based on page importance
        priority = "high" if page_name in ["HomePage", "Dashboard"] else "medium"
        hours = 4 if timeline_preference == "fast" else 6
        
        task = {
            "name": f"Implement {page_name} Page",
            "description": f"Create and integrate {page_name} page",
            "estimated_hours": hours,
            "category": "frontend",
            "priority": priority,
            "dependencies": ["Page Implementation"],
            "subtasks": [
                f"Create {page_name} page structure",
                f"Implement {page_name} functionality",
                f"Add {page_name} routing",
                f"Test {page_name} page",
            ],
        }
        
        tasks.append(task)
    
    return tasks


def _create_task_summary(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    """Create summary statistics for the task list."""
    summary = {
        "total_tasks": len(tasks),
        "by_category": {},
        "by_priority": {},
        "total_estimated_hours": 0,
    }
    
    for task in tasks:
        category = task.get("category", "other")
        priority = task.get("priority", "medium")
        hours = task.get("estimated_hours", 0)
        
        # Count by category
        summary["by_category"][category] = summary["by_category"].get(category, 0) + 1
        
        # Count by priority
        summary["by_priority"][priority] = summary["by_priority"].get(priority, 0) + 1
        
        # Sum total hours
        summary["total_estimated_hours"] += hours
    
    return summary


def _build_dependency_graph(tasks: list[dict[str, Any]]) -> dict[str, Any]:
    """Build dependency graph showing task relationships."""
    graph = {
        "nodes": [],
        "edges": [],
    }
    
    # Create nodes for each task
    for task in tasks:
        graph["nodes"].append({
            "id": task.get("name", ""),
            "category": task.get("category", ""),
            "priority": task.get("priority", ""),
            "estimated_hours": task.get("estimated_hours", 0),
        })
    
    # Create edges for dependencies
    for task in tasks:
        task_name = task.get("name", "")
        dependencies = task.get("dependencies", [])
        
        for dependency in dependencies:
            graph["edges"].append({
                "from": dependency,
                "to": task_name,
                "type": "dependency",
            })
    
    return graph


def _calculate_effort_estimation(tasks: list[dict[str, Any]], team_size: int) -> dict[str, Any]:
    """Calculate effort estimation and timeline projections."""
    total_hours = sum(task.get("estimated_hours", 0) for task in tasks)
    
    # Adjust for team size (with some overhead for coordination)
    if team_size > 1:
        coordination_overhead = 0.2  # 20% overhead for team coordination
        effective_team_size = team_size * (1 - coordination_overhead)
        parallel_hours = total_hours / effective_team_size
    else:
        parallel_hours = total_hours
    
    # Calculate timeline estimates
    hours_per_day = 6  # Effective coding hours per day
    hours_per_week = hours_per_day * 5  # 5-day work week
    
    estimation = {
        "total_hours": total_hours,
        "parallel_hours": int(parallel_hours),
        "team_size": team_size,
        "estimated_days": int(parallel_hours / hours_per_day),
        "estimated_weeks": int(parallel_hours / hours_per_week),
        "by_category": {},
    }
    
    # Break down by category
    for task in tasks:
        category = task.get("category", "other")
        hours = task.get("estimated_hours", 0)
        
        if category not in estimation["by_category"]:
            estimation["by_category"][category] = {
                "total_hours": 0,
                "task_count": 0,
            }
        
        estimation["by_category"][category]["total_hours"] += hours
        estimation["by_category"][category]["task_count"] += 1
    
    return estimation
