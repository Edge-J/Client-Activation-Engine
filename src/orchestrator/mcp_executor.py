"""
MCP Tool Orchestration Executor.

This module provides the enhanced executor specifically for MCP tool execution
with structured results, security validation, and audit logging.
"""

import json
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional
from uuid import UUID, uuid4

from src.core.enums import ProcessingStatus
from src.sandbox.sandbox_runner import (
    SandboxRunner, 
    SandboxResult,
    create_mcp_tool_sandbox,
)


@dataclass
class ToolExecutionContext:
    """Context information for MCP tool execution."""
    workflow_id: UUID
    client_id: Optional[UUID] = None
    tool_name: str = ""
    input_data: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)
    execution_id: UUID = field(default_factory=uuid4)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for logging/serialization."""
        return {
            "workflow_id": str(self.workflow_id),
            "client_id": str(self.client_id) if self.client_id else None,
            "tool_name": self.tool_name,
            "execution_id": str(self.execution_id),
            "metadata": self.metadata,
        }


@dataclass 
class ToolExecutionResult:
    """Structured result of MCP tool execution with detailed status information."""
    success: bool
    output_data: dict[str, Any] = field(default_factory=dict)
    error_message: str = ""
    execution_time: float = 0.0
    status: ProcessingStatus = ProcessingStatus.PENDING
    context: Optional[ToolExecutionContext] = None
    
    # Detailed execution information
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    
    # Security and validation results
    validation_passed: bool = True
    validation_errors: list[str] = field(default_factory=list)
    forbidden_operations: list[str] = field(default_factory=list)
    
    # Output artifacts
    generated_files: list[str] = field(default_factory=list)
    log_entries: list[str] = field(default_factory=list)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "success": self.success,
            "output_data": self.output_data,
            "error_message": self.error_message,
            "execution_time": self.execution_time,
            "status": self.status.value,
            "context": self.context.to_dict() if self.context else None,
            "stdout": self.stdout,
            "stderr": self.stderr,
            "exit_code": self.exit_code,
            "validation_passed": self.validation_passed,
            "validation_errors": self.validation_errors,
            "forbidden_operations": self.forbidden_operations,
            "generated_files": self.generated_files,
            "log_entries": self.log_entries,
        }
    
    @classmethod
    def from_sandbox_result(
        cls,
        sandbox_result: SandboxResult,
        context: Optional[ToolExecutionContext] = None,
        output_data: Optional[dict[str, Any]] = None,
    ) -> "ToolExecutionResult":
        """Create ToolExecutionResult from SandboxResult."""
        return cls(
            success=sandbox_result.success,
            output_data=output_data or {},
            error_message=sandbox_result.stderr,
            execution_time=sandbox_result.execution_time,
            status=sandbox_result.status,
            context=context,
            stdout=sandbox_result.stdout,
            stderr=sandbox_result.stderr,
            exit_code=sandbox_result.exit_code,
        )


class MCPToolExecutor:
    """
    Enhanced executor for running MCP tools with security constraints.
    
    Provides structured execution results, output validation, and
    forbidden operation detection for all MCP tool executions.
    """
    
    def __init__(self, sandbox_runner: Optional[SandboxRunner] = None):
        """
        Initialize executor with optional custom sandbox.
        
        Args:
            sandbox_runner: Custom sandbox runner (defaults to MCP tool sandbox)
        """
        self.sandbox = sandbox_runner or create_mcp_tool_sandbox()
        self.logger = logging.getLogger(__name__)
        self.execution_history: list[ToolExecutionResult] = []
        
    def execute_mcp_tool(
        self,
        tool_module: str,
        function_name: str,
        input_data: dict[str, Any],
        context: Optional[ToolExecutionContext] = None,
    ) -> ToolExecutionResult:
        """
        Execute an MCP tool function with full validation and monitoring.
        
        Args:
            tool_module: MCP tool module name (e.g., "mcp_servers.intake.parse_intake")
            function_name: Function to execute (e.g., "run")
            input_data: Input parameters for the tool
            context: Execution context information
            
        Returns:
            Structured execution result with detailed status
        """
        start_time = time.time()
        
        if not context:
            context = ToolExecutionContext(
                workflow_id=uuid4(),
                tool_name=f"{tool_module}.{function_name}",
                input_data=input_data,
            )
        
        self.logger.info(
            "Executing MCP tool: %s.%s for workflow %s",
            tool_module, function_name, context.workflow_id
        )
        
        # Validate tool module is allowed
        if not self._validate_tool_module(tool_module):
            result = ToolExecutionResult(
                success=False,
                error_message=f"Tool module '{tool_module}' not allowed",
                execution_time=time.time() - start_time,
                status=ProcessingStatus.FAILED,
                context=context,
                validation_passed=False,
                validation_errors=[f"Forbidden tool module: {tool_module}"],
            )
            self.execution_history.append(result)
            return result
        
        # Build execution code
        execution_code = self._build_tool_execution_code(
            tool_module, function_name, input_data
        )
        
        # Execute in sandbox
        sandbox_result = self.sandbox.execute_code(execution_code)
        
        # Parse output and create structured result
        result = self._process_sandbox_result(
            sandbox_result, context, input_data
        )
        
        result.execution_time = time.time() - start_time
        self.execution_history.append(result)
        
        # Log execution details
        self.logger.info(
            "Tool execution completed: success=%s, time=%.3fs, status=%s",
            result.success, result.execution_time, result.status.value
        )
        
        if not result.success:
            self.logger.error(
                "Tool execution failed: %s", result.error_message
            )
        
        return result
    
    def _validate_tool_module(self, tool_module: str) -> bool:
        """Validate that the tool module is allowed."""
        allowed_prefixes = [
            "mcp_servers.intake",
            "mcp_servers.analysis", 
            "mcp_servers.generation",
            "mcp_servers.skills",
        ]
        
        return any(tool_module.startswith(prefix) for prefix in allowed_prefixes)
    
    def _build_tool_execution_code(
        self,
        tool_module: str,
        function_name: str,
        input_data: dict[str, Any],
    ) -> str:
        """Build Python code for executing the tool."""
        # Serialize input data safely
        input_json = json.dumps(input_data, default=str, indent=2)
        
        code = f"""
import json
import sys
from {tool_module} import {function_name}

# Input data
input_data = {input_json}

try:
    # Execute the tool function
    result = {function_name}(input_data)
    
    # Output result as JSON for parsing
    print("=== EXECUTION_RESULT_START ===")
    print(json.dumps(result, default=str, indent=2))
    print("=== EXECUTION_RESULT_END ===")
    
except Exception as e:
    # Output error information
    print("=== EXECUTION_ERROR_START ===", file=sys.stderr)
    print(f"{{\\\"error_type\\\": \\\"{type(e).__name__}\\\", \\\"error_message\\\": \\\"{str(e)}\\\"}}", file=sys.stderr)
    print("=== EXECUTION_ERROR_END ===", file=sys.stderr)
    raise
"""
        
        return code
    
    def _process_sandbox_result(
        self,
        sandbox_result: SandboxResult,
        context: ToolExecutionContext,
        input_data: dict[str, Any],
    ) -> ToolExecutionResult:
        """Process sandbox result into structured execution result."""
        result = ToolExecutionResult.from_sandbox_result(
            sandbox_result, context, {}
        )
        
        # Parse output data from stdout if available
        if sandbox_result.success and sandbox_result.stdout:
            output_data = self._parse_tool_output(sandbox_result.stdout)
            result.output_data = output_data
            
        # Check for forbidden operations in stderr
        forbidden_ops = self._detect_forbidden_operations(
            sandbox_result.stderr
        )
        result.forbidden_operations = forbidden_ops
        
        if forbidden_ops:
            result.validation_passed = False
            result.validation_errors.extend([
                f"Forbidden operation detected: {op}" for op in forbidden_ops
            ])
        
        # Detect generated files
        result.generated_files = self._detect_generated_files(
            sandbox_result.stdout, sandbox_result.stderr
        )
        
        # Capture log entries
        result.log_entries = self._extract_log_entries(
            sandbox_result.stdout, sandbox_result.stderr
        )
        
        return result
    
    def _parse_tool_output(self, stdout: str) -> dict[str, Any]:
        """Parse JSON output from tool execution."""
        try:
            # Look for output markers
            start_marker = "=== EXECUTION_RESULT_START ==="
            end_marker = "=== EXECUTION_RESULT_END ==="
            
            start_idx = stdout.find(start_marker)
            end_idx = stdout.find(end_marker)
            
            if start_idx != -1 and end_idx != -1:
                json_str = stdout[start_idx + len(start_marker):end_idx].strip()
                return json.loads(json_str)
            
            # Fallback: try to parse entire stdout as JSON
            return json.loads(stdout)
            
        except (json.JSONDecodeError, ValueError) as e:
            self.logger.warning("Failed to parse tool output as JSON: %s", e)
            return {"raw_output": stdout}
    
    def _detect_forbidden_operations(self, stderr: str) -> list[str]:
        """Detect forbidden operations from error messages."""
        forbidden_ops = []
        
        # File system violations
        if "file write operation not allowed" in stderr.lower():
            forbidden_ops.append("unauthorized_file_write")
            
        if "import not allowed" in stderr.lower():
            forbidden_ops.append("unauthorized_import")
            
        # Subprocess violations
        if "subprocess" in stderr.lower():
            forbidden_ops.append("subprocess_usage")
            
        # Network access violations
        if "network" in stderr.lower() or "socket" in stderr.lower():
            forbidden_ops.append("network_access")
            
        return forbidden_ops
    
    def _detect_generated_files(self, stdout: str, stderr: str) -> list[str]:
        """Detect files generated during execution."""
        generated_files = []
        
        # Look for file creation patterns in output
        output_text = f"{stdout}\n{stderr}"
        
        # Common patterns for file generation
        patterns = [
            r"saved to ([^\s]+)",
            r"written to ([^\s]+)", 
            r"created file ([^\s]+)",
            r"output file: ([^\s]+)",
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, output_text, re.IGNORECASE)
            generated_files.extend(matches)
            
        return list(set(generated_files))  # Remove duplicates
    
    def _extract_log_entries(self, stdout: str, stderr: str) -> list[str]:
        """Extract log entries from execution output."""
        log_entries = []
        
        # Split output into lines and filter for log-like entries
        all_lines = stdout.split("\n") + stderr.split("\n")
        
        for line in all_lines:
            line = line.strip()
            if not line:
                continue
                
            # Look for log-like patterns
            if any(indicator in line.lower() for indicator in [
                "info:", "debug:", "warning:", "error:", "log:",
                "[info]", "[debug]", "[warning]", "[error]"
            ]):
                log_entries.append(line)
                
        return log_entries
    
    def get_execution_history(
        self, 
        workflow_id: Optional[UUID] = None,
        limit: Optional[int] = None,
    ) -> list[ToolExecutionResult]:
        """
        Get execution history with optional filtering.
        
        Args:
            workflow_id: Filter by specific workflow
            limit: Maximum number of results to return
            
        Returns:
            List of execution results
        """
        history = self.execution_history
        
        if workflow_id:
            history = [
                result for result in history
                if result.context and result.context.workflow_id == workflow_id
            ]
        
        if limit:
            history = history[-limit:]
            
        return history
    
    def get_execution_stats(self) -> dict[str, Any]:
        """Get statistics about tool executions."""
        total_executions = len(self.execution_history)
        successful_executions = sum(1 for result in self.execution_history if result.success)
        
        if total_executions == 0:
            return {
                "total_executions": 0,
                "success_rate": 0.0,
                "average_execution_time": 0.0,
                "most_common_errors": [],
            }
        
        success_rate = successful_executions / total_executions
        avg_execution_time = sum(
            result.execution_time for result in self.execution_history
        ) / total_executions
        
        # Count error types
        error_counts: dict[str, int] = {}
        for result in self.execution_history:
            if not result.success and result.error_message:
                error_type = result.error_message.split(":")[0]
                error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        most_common_errors = sorted(
            error_counts.items(), key=lambda x: x[1], reverse=True
        )[:5]
        
        return {
            "total_executions": total_executions,
            "successful_executions": successful_executions,
            "success_rate": success_rate,
            "average_execution_time": avg_execution_time,
            "most_common_errors": most_common_errors,
        }
    
    def persist_execution_history(
        self, 
        output_path: str = "logs/tool_execution_history.json"
    ) -> None:
        """Persist execution history to file for audit trail."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        history_data = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_executions": len(self.execution_history),
            "executions": [result.to_dict() for result in self.execution_history],
            "stats": self.get_execution_stats(),
        }
        
        with output_file.open("w", encoding="utf-8") as f:
            json.dump(history_data, f, indent=2, default=str)
        
        self.logger.info(
            "Persisted execution history: %d entries to %s",
            len(self.execution_history), output_path
        )


def create_mcp_executor() -> MCPToolExecutor:
    """Create MCP tool executor with default sandbox."""
    return MCPToolExecutor()


def create_permissive_mcp_executor() -> MCPToolExecutor:
    """Create MCP tool executor with permissive sandbox for development."""
    from src.sandbox.sandbox_runner import create_permissive_sandbox
    return MCPToolExecutor(create_permissive_sandbox())
