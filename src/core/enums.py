"""
Core enumerations for the Client Activation Engine.

This module contains shared enums used throughout the application for
maintaining consistency across different components.
"""

from enum import Enum, auto


class ClientTier(Enum):
    """Client service tier levels determining available features and limits."""
    STARTER = "starter"
    BUSINESS = "business"
    PREMIUM = "premium"


class AssetType(Enum):
    """Types of assets that can be generated for clients."""
    DOCUMENTATION = "documentation"
    CODE = "code"
    CONFIGURATION = "configuration"
    TEMPLATE = "template"
    SPECIFICATION = "specification"
    DIAGRAM = "diagram"
    REPORT = "report"


class MissingInfoCategory(Enum):
    """Categories of missing information that need to be collected."""
    TECHNICAL_REQUIREMENTS = "technical_requirements"
    BUSINESS_LOGIC = "business_logic"
    INTEGRATION_DETAILS = "integration_details"
    AUTHENTICATION = "authentication"
    DATA_SCHEMA = "data_schema"
    UI_SPECIFICATIONS = "ui_specifications"
    DEPLOYMENT_CONFIG = "deployment_config"
    PERFORMANCE_REQUIREMENTS = "performance_requirements"


class ProcessingStatus(Enum):
    """Status of processing workflows."""
    PENDING = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    FAILED = auto()
    PAUSED = auto()
    CANCELLED = auto()


class ToolCategory(Enum):
    """Categories of tools available in the MCP servers."""
    INTAKE = "intake"
    ANALYSIS = "analysis"
    GENERATION = "generation"
    SKILLS = "skills"


class ValidationLevel(Enum):
    """Validation strictness levels."""
    STRICT = "strict"
    MODERATE = "moderate"
    LENIENT = "lenient"
