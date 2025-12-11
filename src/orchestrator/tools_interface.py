"""
Tools interface for MCP server discovery and execution.

This module provides the interface for discovering and executing tools
from the MCP servers directory structure.
"""

from pathlib import Path
from typing import Any, Protocol

from ..core.enums import ToolCategory
from ..core.schema_definitions import ValidationResult


class ToolInfo:
    """Information about an available tool."""
    
    def __init__(
        self,
        name: str,
        category: ToolCategory,
        description: str,
        module_path: str,
        parameters: dict[str, Any] | None = None,
    ):
        self.name = name
        self.category = category
        self.description = description
        self.module_path = module_path
        self.parameters = parameters or {}


class ToolInterface(Protocol):
    """Protocol for tool discovery and execution."""
    
    def discover_tools(self) -> list[ToolInfo]:
        """Discover all available tools."""
        ...
    
    def get_tool_by_name(self, name: str) -> ToolInfo | None:
        """Get tool information by name."""
        ...
    
    def execute_tool(
        self, 
        tool_name: str, 
        parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """Execute a tool with given parameters."""
        ...
    
    def validate_tool_parameters(
        self, 
        tool_name: str, 
        parameters: dict[str, Any]
    ) -> ValidationResult:
        """Validate parameters for a tool."""
        ...


class MCPToolsInterface:
    """
    Interface for discovering and executing MCP tools.
    
    This class provides a unified interface for interacting with tools
    distributed across the MCP servers directory structure.
    """
    
    def __init__(self, mcp_servers_path: str = "mcp_servers"):
        """
        Initialize the tools interface.
        
        Args:
            mcp_servers_path: Path to MCP servers directory
        """
        self.mcp_servers_path = Path(mcp_servers_path)
        self._tool_cache: dict[str, ToolInfo] = {}
        self._discovery_complete = False
        
    def discover_tools(self) -> list[ToolInfo]:
        """
        Discover all available tools from MCP servers.
        
        Returns:
            List of discovered tool information
        """
        if self._discovery_complete:
            return list(self._tool_cache.values())
            
        tools = []
        
        # Scan each category directory
        for category in ToolCategory:
            category_path = self.mcp_servers_path / category.value
            if category_path.exists():
                category_tools = self._discover_tools_in_category(
                    category_path, category
                )
                tools.extend(category_tools)
                
        # Cache discovered tools
        for tool in tools:
            self._tool_cache[tool.name] = tool
            
        self._discovery_complete = True
        return tools
    
    def get_tool_by_name(self, name: str) -> ToolInfo | None:
        """
        Get tool information by name.
        
        Args:
            name: Tool name to search for
            
        Returns:
            ToolInfo if found, None otherwise
        """
        if not self._discovery_complete:
            self.discover_tools()
            
        return self._tool_cache.get(name)
    
    def execute_tool(
        self, 
        tool_name: str, 
        parameters: dict[str, Any]
    ) -> dict[str, Any]:
        """
        Execute a tool with given parameters.
        
        Args:
            tool_name: Name of tool to execute
            parameters: Parameters to pass to tool
            
        Returns:
            Tool execution results
            
        Raises:
            ValueError: If tool is not found
            RuntimeError: If tool execution fails
        """
        tool = self.get_tool_by_name(tool_name)
        if not tool:
            raise ValueError(f"Tool not found: {tool_name}")
            
        # TODO: Implement actual tool execution
        # This is a placeholder for future implementation
        return {
            "tool_name": tool_name,
            "category": tool.category.value,
            "status": "executed",
            "parameters": parameters,
            "result": f"Mock execution result for {tool_name}",
        }
    
    def validate_tool_parameters(
        self, 
        tool_name: str, 
        parameters: dict[str, Any]
    ) -> ValidationResult:
        """
        Validate parameters for a tool.
        
        Args:
            tool_name: Name of tool to validate parameters for
            parameters: Parameters to validate
            
        Returns:
            ValidationResult with validation status
        """
        tool = self.get_tool_by_name(tool_name)
        if not tool:
            return ValidationResult(
                is_valid=False,
                errors=[f"Tool not found: {tool_name}"],
                warnings=[],
                score=0.0,
            )
        
        # TODO: Implement parameter validation based on tool schema
        # For now, basic validation
        errors = []
        warnings = []
        
        # Check if required parameters are provided
        required_params = tool.parameters.get("required", [])
        for param in required_params:
            if param not in parameters:
                errors.append(f"Required parameter missing: {param}")
        
        # Check for unexpected parameters
        allowed_params = set(tool.parameters.get("properties", {}).keys())
        for param in parameters:
            if param not in allowed_params:
                warnings.append(f"Unexpected parameter: {param}")
        
        is_valid = len(errors) == 0
        score = 1.0 if is_valid else 0.0
        
        return ValidationResult(
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            score=score,
        )
    
    def get_tools_by_category(self, category: ToolCategory) -> list[ToolInfo]:
        """
        Get all tools in a specific category.
        
        Args:
            category: Tool category to filter by
            
        Returns:
            List of tools in the specified category
        """
        if not self._discovery_complete:
            self.discover_tools()
            
        return [tool for tool in self._tool_cache.values() 
                if tool.category == category]
    
    def refresh_discovery(self) -> None:
        """Refresh tool discovery, clearing cache."""
        self._tool_cache.clear()
        self._discovery_complete = False
        self.discover_tools()
    
    def _discover_tools_in_category(
        self, 
        category_path: Path, 
        category: ToolCategory
    ) -> list[ToolInfo]:
        """
        Discover tools in a specific category directory.
        
        Args:
            category_path: Path to category directory
            category: Tool category
            
        Returns:
            List of tools found in the category
        """
        tools = []
        
        # Look for Python modules in the category directory
        for py_file in category_path.glob("*.py"):
            if py_file.name.startswith("__"):
                continue  # Skip __init__.py and similar
                
            # Create tool info from module
            tool_name = f"{category.value}.{py_file.stem}"
            tool = ToolInfo(
                name=tool_name,
                category=category,
                description=f"Tool from {py_file.name}",
                module_path=str(py_file),
                parameters={
                    "properties": {},
                    "required": [],
                },
            )
            tools.append(tool)
        
        return tools
    
    def get_discovery_summary(self) -> dict[str, Any]:
        """
        Get a summary of tool discovery results.
        
        Returns:
            Dictionary with discovery statistics
        """
        if not self._discovery_complete:
            self.discover_tools()
            
        category_counts = {}
        for category in ToolCategory:
            category_tools = self.get_tools_by_category(category)
            category_counts[category.value] = len(category_tools)
        
        return {
            "total_tools": len(self._tool_cache),
            "categories": category_counts,
            "discovery_path": str(self.mcp_servers_path),
            "discovery_complete": self._discovery_complete,
        }


def create_tools_interface() -> MCPToolsInterface:
    """
    Create a new tools interface instance.
    
    Returns:
        Configured MCPToolsInterface
    """
    return MCPToolsInterface("mcp_servers")
