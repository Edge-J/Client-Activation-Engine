"""
Deterministic Lovable specification generator.

This tool generates comprehensive Lovable project specifications
from analyzed requirements and assets using template-based generation.
"""

import logging
from typing import Any
from datetime import datetime

logger = logging.getLogger(__name__)

# Lovable specification templates
LOVABLE_SPEC_TEMPLATE = {
    "project_info": {
        "name": "{project_name}",
        "description": "{project_description}",
        "type": "{project_type}",
        "framework": "React",
        "styling": "Tailwind CSS",
        "backend": "{backend_type}",
        "database": "{database_type}",
    },
    "pages": [],
    "components": [],
    "apis": [],
    "database_schema": [],
    "styling_guidelines": {},
    "deployment_config": {},
}

# Component templates for Lovable
COMPONENT_TEMPLATES = {
    "navigation": {
        "name": "Navigation",
        "type": "component", 
        "description": "Main navigation component",
        "props": ["user", "onLogout"],
        "features": ["responsive", "dropdown menus", "active state"],
    },
    "form": {
        "name": "ContactForm",
        "type": "component",
        "description": "Contact form with validation",
        "props": ["onSubmit", "initialData"],
        "features": ["validation", "error handling", "loading states"],
    },
    "modal": {
        "name": "Modal",
        "type": "component", 
        "description": "Reusable modal dialog",
        "props": ["isOpen", "onClose", "title", "children"],
        "features": ["overlay", "animation", "keyboard navigation"],
    },
}

# Page templates
PAGE_TEMPLATES = {
    "landing": {
        "name": "HomePage",
        "route": "/",
        "description": "Main landing page",
        "components": ["Hero", "Features", "CallToAction"],
        "sections": ["header", "hero", "features", "testimonials", "footer"],
    },
    "about": {
        "name": "AboutPage", 
        "route": "/about",
        "description": "About us page",
        "components": ["CompanyInfo", "TeamSection", "Values"],
        "sections": ["company_story", "team", "values", "contact_info"],
    },
    "contact": {
        "name": "ContactPage",
        "route": "/contact",
        "description": "Contact information and form",
        "components": ["ContactForm", "ContactInfo", "Map"],
        "sections": ["contact_form", "contact_details", "location"],
    },
    "dashboard": {
        "name": "Dashboard",
        "route": "/dashboard", 
        "description": "User dashboard",
        "components": ["StatsCards", "ActivityFeed", "QuickActions"],
        "sections": ["stats", "recent_activity", "quick_actions"],
        "auth_required": True,
    },
}

# API endpoint templates
API_TEMPLATES = {
    "auth": [
        {"method": "POST", "endpoint": "/auth/login", "description": "User login"},
        {"method": "POST", "endpoint": "/auth/register", "description": "User registration"}, 
        {"method": "POST", "endpoint": "/auth/logout", "description": "User logout"},
        {"method": "GET", "endpoint": "/auth/profile", "description": "Get user profile"},
    ],
    "users": [
        {"method": "GET", "endpoint": "/users", "description": "List users"},
        {"method": "GET", "endpoint": "/users/:id", "description": "Get user by ID"},
        {"method": "PUT", "endpoint": "/users/:id", "description": "Update user"},
        {"method": "DELETE", "endpoint": "/users/:id", "description": "Delete user"},
    ],
    "data": [
        {"method": "GET", "endpoint": "/api/items", "description": "List items"},
        {"method": "POST", "endpoint": "/api/items", "description": "Create item"},
        {"method": "PUT", "endpoint": "/api/items/:id", "description": "Update item"},
        {"method": "DELETE", "endpoint": "/api/items/:id", "description": "Delete item"},
    ],
}


def get_tool_metadata() -> dict[str, Any]:
    """Get metadata for the Lovable spec generator tool."""
    return {
        "name": "generate_lovable_spec",
        "description": "Generate Lovable project specification from requirements and assets",
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
                "business_context": {
                    "type": "object", 
                    "description": "Business type and project context",
                    "default": {},
                },
                "project_name": {
                    "type": "string",
                    "description": "Name of the project",
                    "default": "New Project",
                },
                "spec_style": {
                    "type": "string",
                    "enum": ["minimal", "standard", "comprehensive"],
                    "description": "Level of detail in the specification",
                    "default": "standard",
                },
            },
            "required": ["requirements", "assets"],
        },
        "output_schema": {
            "type": "object",
            "properties": {
                "lovable_spec": {
                    "type": "object",
                    "description": "Complete Lovable project specification",
                },
                "component_list": {
                    "type": "array",
                    "description": "List of React components to create",
                },
                "page_structure": {
                    "type": "object",
                    "description": "Page hierarchy and routing structure",
                },
                "api_endpoints": {
                    "type": "array",
                    "description": "Backend API endpoints",
                },
                "generation_summary": {
                    "type": "object",
                    "description": "Summary of generated specification",
                },
            },
        },
        "dependencies": ["extract_assets"],
    }


def run(parameters: dict[str, Any]) -> dict[str, Any]:
    """
    Generate Lovable project specification.
    
    Args:
        parameters: Tool execution parameters
        
    Returns:
        Dictionary containing Lovable specification and components
    """
    requirements = parameters.get("requirements", {})
    assets = parameters.get("assets", {})
    business_context = parameters.get("business_context", {})
    project_name = parameters.get("project_name", "New Project")
    spec_style = parameters.get("spec_style", "standard")
    
    if not requirements or not assets:
        return {
            "error": "Requirements and assets must be provided for spec generation",
            "lovable_spec": {},
            "component_list": [],
            "page_structure": {},
            "api_endpoints": [],
            "generation_summary": {},
        }
    
    logger.info("Generating Lovable spec with %s style", spec_style)
    
    business_type = business_context.get("business_type", "general")
    
    # Generate different parts of the specification
    lovable_spec = _create_base_spec(project_name, business_type, requirements)
    component_list = _generate_components(assets, requirements, spec_style)
    page_structure = _generate_page_structure(assets, requirements, spec_style)
    api_endpoints = _generate_api_endpoints(assets, requirements)
    
    # Populate the full specification
    lovable_spec["pages"] = page_structure.get("pages", [])
    lovable_spec["components"] = component_list
    lovable_spec["apis"] = api_endpoints
    lovable_spec["database_schema"] = _generate_database_schema(assets)
    lovable_spec["styling_guidelines"] = _generate_styling_guidelines(spec_style)
    lovable_spec["deployment_config"] = _generate_deployment_config(assets)
    
    # Create generation summary
    generation_summary = {
        "project_name": project_name,
        "pages_count": len(page_structure.get("pages", [])),
        "components_count": len(component_list),
        "api_endpoints_count": len(api_endpoints),
        "spec_style": spec_style,
        "business_type": business_type,
        "generated_at": datetime.now().isoformat(),
    }
    
    return {
        "lovable_spec": lovable_spec,
        "component_list": component_list,
        "page_structure": page_structure,
        "api_endpoints": api_endpoints,
        "generation_summary": generation_summary,
        "generation_metadata": {
            "tool": "generate_lovable_spec",
            "version": "1.0.0",
            "spec_style": spec_style,
        },
    }


def _create_base_spec(
    project_name: str, 
    business_type: str, 
    requirements: dict[str, Any],
) -> dict[str, Any]:
    """Create the base Lovable specification structure."""
    spec = LOVABLE_SPEC_TEMPLATE.copy()
    
    # Set project information
    spec["project_info"]["name"] = project_name
    spec["project_info"]["description"] = f"A {business_type} application built with React"
    spec["project_info"]["type"] = business_type
    
    # Determine backend and database types
    functional_reqs = requirements.get("functional_requirements", [])
    has_auth = any("auth" in req.get("category", "").lower() for req in functional_reqs)
    has_complex_data = len([req for req in functional_reqs if "data" in req.get("category", "").lower()]) > 2
    
    spec["project_info"]["backend"] = "Express.js" if has_auth or has_complex_data else "Static"
    spec["project_info"]["database"] = "PostgreSQL" if has_complex_data else "Local Storage"
    
    return spec


def _generate_components(
    assets: dict[str, Any], 
    requirements: dict[str, Any], 
    spec_style: str,
) -> list[dict[str, Any]]:
    """Generate React component specifications."""
    components = []
    
    frontend_assets = assets.get("frontend_assets", [])
    
    # Extract component assets
    component_assets = [
        asset for asset in frontend_assets 
        if asset.get("category") == "component"
    ]
    
    # Generate components based on assets
    for asset in component_assets:
        component_name = asset.get("name", "")
        
        # Match to template or create custom
        if "navigation" in component_name.lower() or "menu" in component_name.lower():
            component = COMPONENT_TEMPLATES["navigation"].copy()
        elif "form" in component_name.lower():
            component = COMPONENT_TEMPLATES["form"].copy()
            component["name"] = component_name.replace(" ", "")
        elif "modal" in component_name.lower() or "dialog" in component_name.lower():
            component = COMPONENT_TEMPLATES["modal"].copy()
        else:
            # Create custom component
            component = {
                "name": component_name.replace(" ", ""),
                "type": "component",
                "description": f"Custom {component_name.lower()}",
                "props": ["className", "children"],
                "features": ["responsive", "accessible"],
            }
        
        components.append(component)
    
    # Add essential components if not present
    essential_components = ["Navigation", "Footer", "LoadingSpinner"]
    existing_names = [comp.get("name", "") for comp in components]
    
    for essential in essential_components:
        if essential not in existing_names and spec_style != "minimal":
            components.append({
                "name": essential,
                "type": "component",
                "description": f"Essential {essential.lower()} component",
                "props": ["className"],
                "features": ["responsive"],
            })
    
    return components


def _generate_page_structure(
    assets: dict[str, Any], 
    requirements: dict[str, Any], 
    spec_style: str,
) -> dict[str, Any]:
    """Generate page structure and routing."""
    pages = []
    
    frontend_assets = assets.get("frontend_assets", [])
    
    # Extract page assets
    page_assets = [
        asset for asset in frontend_assets 
        if asset.get("category") == "web_page"
    ]
    
    functional_reqs = requirements.get("functional_requirements", [])
    has_auth = any("auth" in req.get("category", "").lower() for req in functional_reqs)
    
    # Generate pages based on assets
    for asset in page_assets:
        page_name = asset.get("name", "")
        
        # Match to template
        if "homepage" in page_name.lower() or "landing" in page_name.lower():
            page = PAGE_TEMPLATES["landing"].copy()
        elif "about" in page_name.lower():
            page = PAGE_TEMPLATES["about"].copy()
        elif "contact" in page_name.lower():
            page = PAGE_TEMPLATES["contact"].copy()
        elif "dashboard" in page_name.lower():
            page = PAGE_TEMPLATES["dashboard"].copy()
        else:
            # Create custom page
            route_name = page_name.lower().replace(" ", "-").replace("/", "")
            page = {
                "name": page_name.replace(" ", ""),
                "route": f"/{route_name}",
                "description": f"Custom {page_name.lower()}",
                "components": ["PageHeader", "PageContent"],
                "sections": ["header", "content"],
            }
        
        # Add auth requirement if needed
        if has_auth and ("dashboard" in page_name.lower() or "profile" in page_name.lower()):
            page["auth_required"] = True
        
        pages.append(page)
    
    # Ensure essential pages exist
    essential_pages = ["HomePage"]
    existing_pages = [page.get("name", "") for page in pages]
    
    if "HomePage" not in existing_pages:
        pages.insert(0, PAGE_TEMPLATES["landing"].copy())
    
    return {
        "pages": pages,
        "routing_type": "React Router",
        "auth_protection": has_auth,
    }


def _generate_api_endpoints(assets: dict[str, Any], requirements: dict[str, Any]) -> list[dict[str, Any]]:
    """Generate API endpoint specifications."""
    endpoints = []
    
    backend_assets = assets.get("backend_assets", [])
    functional_reqs = requirements.get("functional_requirements", [])
    
    # Check for different API needs
    has_auth = any("auth" in req.get("category", "").lower() for req in functional_reqs)
    has_user_mgmt = any("user" in asset.get("name", "").lower() for asset in backend_assets)
    has_data_mgmt = any("data" in req.get("category", "").lower() for req in functional_reqs)
    
    if has_auth:
        endpoints.extend(API_TEMPLATES["auth"])
    
    if has_user_mgmt:
        endpoints.extend(API_TEMPLATES["users"])
    
    if has_data_mgmt:
        endpoints.extend(API_TEMPLATES["data"])
    
    return endpoints


def _generate_database_schema(assets: dict[str, Any]) -> list[dict[str, Any]]:
    """Generate database schema specifications."""
    schema = []
    
    backend_assets = assets.get("backend_assets", [])
    
    # Extract database assets
    db_assets = [
        asset for asset in backend_assets 
        if asset.get("category") == "database"
    ]
    
    for asset in db_assets:
        table_name = asset.get("name", "")
        
        if "user" in table_name.lower():
            schema.append({
                "table": "users",
                "fields": [
                    {"name": "id", "type": "uuid", "primary": True},
                    {"name": "email", "type": "string", "unique": True},
                    {"name": "password_hash", "type": "string"},
                    {"name": "created_at", "type": "timestamp"},
                    {"name": "updated_at", "type": "timestamp"},
                ],
            })
        elif "data" in table_name.lower() or "item" in table_name.lower():
            schema.append({
                "table": "items",
                "fields": [
                    {"name": "id", "type": "uuid", "primary": True},
                    {"name": "name", "type": "string"},
                    {"name": "description", "type": "text"},
                    {"name": "user_id", "type": "uuid", "foreign_key": "users.id"},
                    {"name": "created_at", "type": "timestamp"},
                ],
            })
    
    return schema


def _generate_styling_guidelines(spec_style: str) -> dict[str, Any]:
    """Generate Tailwind CSS styling guidelines."""
    guidelines = {
        "framework": "Tailwind CSS",
        "color_scheme": {
            "primary": "blue-600",
            "secondary": "gray-600", 
            "accent": "green-500",
            "background": "white",
        },
        "typography": {
            "font_family": "Inter, system-ui, sans-serif",
            "headings": "font-bold tracking-tight",
            "body": "font-normal leading-relaxed",
        },
        "spacing": {
            "container": "max-w-7xl mx-auto px-4",
            "section": "py-16",
            "component": "p-6",
        },
    }
    
    if spec_style == "comprehensive":
        guidelines["animations"] = {
            "transitions": "transition-all duration-200 ease-in-out",
            "hover_effects": "hover:scale-105 hover:shadow-lg",
        }
        guidelines["responsive"] = {
            "mobile": "sm:max-md:",
            "tablet": "md:max-lg:",
            "desktop": "lg:",
        }
    
    return guidelines


def _generate_deployment_config(assets: dict[str, Any]) -> dict[str, Any]:
    """Generate deployment configuration."""
    infrastructure_assets = assets.get("infrastructure_assets", [])
    
    has_server = any("server" in asset.get("name", "").lower() for asset in infrastructure_assets)
    has_ssl = any("ssl" in asset.get("name", "").lower() for asset in infrastructure_assets)
    
    config = {
        "platform": "Vercel" if not has_server else "Railway",
        "build_command": "npm run build",
        "output_directory": "dist",
        "node_version": "18",
        "environment_variables": [
            "DATABASE_URL",
            "JWT_SECRET",
            "API_BASE_URL",
        ],
    }
    
    if has_ssl:
        config["ssl"] = True
        config["custom_domain"] = True
    
    return config
