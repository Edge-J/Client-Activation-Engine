"""
Enhanced executor interface for orchestration workflows.

This module provides structured execution results and integrates with
the hardened sandbox runner for secure MCP tool execution.
"""

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Protocol
from uuid import UUID, uuid4

from src.core.enums import ProcessingStatus
from src.core.schema_definitions import BaseSchema, ValidationResult
from src.sandbox.sandbox_runner import SandboxRunner, create_mcp_tool_sandbox


class ExecutorInterface(Protocol):
    """Protocol for code execution in orchestration workflows."""
    
    def submit_code(
        self, 
        code: str, 
        context: dict[str, Any] | None = None
    ) -> SandboxResult:
        """Submit Python code for execution."""
        ...
    
    def validate_code(self, code: str) -> ValidationResult:
        """Validate code before execution."""
        ...
    
    def get_execution_history(self) -> list[SandboxResult]:
        """Get history of executed code snippets."""
        ...
    
    def cleanup_resources(self) -> None:
        """Clean up any resources used by the executor."""
        ...


class SandboxExecutor:
    """
    Concrete implementation of code execution using sandbox runner.
    
    This class provides a safe interface for the orchestration loop to
    execute dynamically generated Python code with proper error handling
    and resource management.
    """
    
    def __init__(self, constraints: SandboxConstraints | None = None):
        """
        Initialize the executor with sandbox constraints.
        
        Args:
            constraints: Sandbox execution limits and permissions
        """
        self.constraints = constraints or SandboxConstraints(
            timeout_seconds=30,
            max_memory_mb=512,
            allow_file_writes=True,  # Allow writes to output directory
            output_directory="/workspace/data/output",
        )
        self.sandbox = SandboxRunner(self.constraints)
        self.execution_history: list[SandboxResult] = []
        
    def submit_code(
        self, 
        code: str, 
        context: dict[str, Any] | None = None
    ) -> SandboxResult:
        """
        Submit Python code for execution in sandbox.
        
        Args:
            code: Python code to execute
            context: Optional execution context (currently unused)
            
        Returns:
            SandboxResult with execution details
            
        Note:
            All file writes are restricted to the configured output directory.
            The executor ensures no file operations occur outside this boundary.
        """
        # Add context setup if provided
        if context:
            context_setup = self._prepare_context_code(context)
            full_code = f"{context_setup}\n\n{code}"
        else:
            full_code = code
            
        # Execute in sandbox
        result = self.sandbox.execute_code(full_code)
        
        # Store in history
        self.execution_history.append(result)
        
        # Log execution details (placeholder for future logging integration)
        self._log_execution(result, context)
        
        return result
    
    def validate_code(self, code: str) -> ValidationResult:
        """
        Validate code before execution.
        
        Args:
            code: Python code to validate
            
        Returns:
            ValidationResult with validation status
        """
        is_valid, issues = self.sandbox.validate_code(code)
        
        return ValidationResult(
            is_valid=is_valid,
            errors=issues if not is_valid else [],
            warnings=[],
            score=1.0 if is_valid else 0.0,
        )
    
    def get_execution_history(self) -> list[SandboxResult]:
        """
        Get history of executed code snippets.
        
        Returns:
            List of all previous execution results
        """
        return self.execution_history.copy()
    
    def cleanup_resources(self) -> None:
        """
        Clean up any resources used by the executor.
        
        This method should be called when the executor is no longer needed
        to ensure proper cleanup of temporary files and resources.
        """
        # Clear execution history to free memory
        self.execution_history.clear()
        
        # Additional cleanup could be added here for future resource management
        
    def get_execution_stats(self) -> dict[str, Any]:
        """
        Get execution statistics.
        
        Returns:
            Dictionary with execution metrics
        """
        if not self.execution_history:
            return {
                "total_executions": 0,
                "success_rate": 0.0,
                "average_execution_time": 0.0,
                "total_execution_time": 0.0,
            }
        
        successful = sum(1 for result in self.execution_history if result.success)
        total_time = sum(result.execution_time for result in self.execution_history)
        
        return {
            "total_executions": len(self.execution_history),
            "success_rate": successful / len(self.execution_history),
            "average_execution_time": total_time / len(self.execution_history),
            "total_execution_time": total_time,
        }
    
    def _prepare_context_code(self, context: dict[str, Any]) -> str:
        """
        Prepare code to set up execution context.
        
        Args:
            context: Context variables to make available
            
        Returns:
            Python code to set up context
        """
        context_lines = []
        context_lines.append("# Context setup")
        
        for key, value in context.items():
            if isinstance(value, str):
                context_lines.append(f'{key} = "{value}"')
            elif isinstance(value, (int, float, bool)):
                context_lines.append(f"{key} = {value}")
            elif isinstance(value, (list, dict)):
                context_lines.append(f"{key} = {repr(value)}")
            else:
                # For complex objects, convert to string representation
                context_lines.append(f'{key} = "{str(value)}"')
        
        return "\n".join(context_lines)
    
    def _log_execution(self, result: SandboxResult, context: dict[str, Any] | None) -> None:
        """
        Log execution details for debugging and monitoring.
        
        Args:
            result: Execution result to log
            context: Execution context that was used
            
        Note:
            This is a placeholder for future logging integration.
        """
        # Future implementation would integrate with the logging system
        # For now, this serves as a placeholder for execution tracking
        pass


def create_executor_for_orchestrator() -> SandboxExecutor:
    """
    Create a properly configured executor for orchestration workflows.
    
    Returns:
        SandboxExecutor configured for orchestration use
    """
    constraints = SandboxConstraints(
        timeout_seconds=60,  # Longer timeout for orchestration tasks
        max_memory_mb=1024,  # More memory for complex operations
        allow_file_writes=True,
        output_directory="/workspace/data/output",
        allowed_imports=[
            "pandas", "numpy", "matplotlib", "seaborn", "plotly",
            "requests", "json", "csv", "datetime", "pathlib", "yaml",
        ],
    )
    
    return SandboxExecutor(constraints)
