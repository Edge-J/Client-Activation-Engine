"""
Sandbox Runner for secure Python code execution.

This module provides a safe environment for executing dynamically generated
Python code with controlled access to imports and file system operations.
"""

import ast
import importlib
import io
import json
import logging
import os
import resource
import signal
import subprocess
import sys
import tempfile
import time
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from types import ModuleType
from typing import Any, Dict, List, NamedTuple, Optional, Set

from ..core.enums import ProcessingStatus


class SandboxResult(NamedTuple):
    """Result of sandbox execution."""
    success: bool
    stdout: str
    stderr: str
    exit_code: int
    execution_time: float
    status: ProcessingStatus


class SandboxConstraints:
    """Configuration for sandbox execution limits and security constraints."""
    
    def __init__(
        self,
        timeout_seconds: int = 30,
        max_memory_mb: int = 512,
        max_cpu_seconds: int = 15,
        max_recursion_depth: int = 100,
        allowed_imports: list[str] | None = None,
        allow_file_writes: bool = False,
        output_directory: str | None = None,
        allowed_builtins: set[str] | None = None,
        log_outputs: bool = True,
        capture_print_outputs: bool = True,
    ):
        self.timeout_seconds = timeout_seconds
        self.max_memory_mb = max_memory_mb
        self.max_cpu_seconds = max_cpu_seconds
        self.max_recursion_depth = max_recursion_depth
        self.allowed_imports = allowed_imports or [
            "json", "re", "datetime", "pathlib", "typing", "dataclasses",
            "collections", "itertools", "functools", "operator",
            # Only allow mcp_servers modules for tool execution
            "mcp_servers", "mcp_servers.intake", "mcp_servers.analysis", 
            "mcp_servers.generation", "mcp_servers.skills",
        ]
        self.allow_file_writes = allow_file_writes
        self.output_directory = output_directory or "/workspace/data/output"
        self.allowed_builtins = allowed_builtins or {
            # Safe builtins only
            "abs", "all", "any", "bool", "callable", "chr", "dict", "dir",
            "enumerate", "filter", "float", "format", "frozenset", "getattr",
            "hasattr", "hash", "hex", "id", "int", "isinstance", "issubclass",
            "iter", "len", "list", "map", "max", "min", "next", "oct", "ord",
            "pow", "print", "range", "repr", "reversed", "round", "set",
            "slice", "sorted", "str", "sum", "tuple", "type", "zip",
            # Exceptions
            "BaseException", "Exception", "ValueError", "TypeError", "KeyError",
            "IndexError", "AttributeError", "RuntimeError", "NotImplementedError",
        }
        self.log_outputs = log_outputs
        self.capture_print_outputs = capture_print_outputs


class RestrictedImportHook:
    """Custom import hook that only allows specified modules."""
    
    def __init__(self, allowed_modules: set[str]):
        self.allowed_modules = allowed_modules
        self.original_import = None
        
    def __call__(self, name: str, *args, **kwargs):
        """Custom import function that filters allowed modules."""
        # Allow mcp_servers.* modules specifically
        if name.startswith("mcp_servers"):
            return self.original_import(name, *args, **kwargs)
            
        # Check base module name against allowlist
        base_module = name.split(".")[0]
        if base_module not in self.allowed_modules:
            raise ImportError(
                f"Import of '{name}' not allowed in sandbox environment. "
                f"Only mcp_servers.* and basic stdlib modules are permitted."
            )
            
        return self.original_import(name, *args, **kwargs)
    
    def install(self):
        """Install the import hook."""
        import builtins
        self.original_import = builtins.__import__
        builtins.__import__ = self
        
    def uninstall(self):
        """Remove the import hook."""
        if self.original_import:
            import builtins
            builtins.__import__ = self.original_import


class SandboxRunner:
    """Secure Python code execution environment with hardened constraints."""
    
    def __init__(self, constraints: SandboxConstraints | None = None):
        self.constraints = constraints or SandboxConstraints()
        self.logger = logging.getLogger(__name__)
        self._captured_outputs: list[str] = []
        
    def validate_code(self, code: str) -> tuple[bool, list[str]]:
        """
        Validate code for security and allowed operations.
        
        Args:
            code: Python code to validate
            
        Returns:
            Tuple of (is_valid, list_of_issues)
        """
        issues = []
        
        # Check for dangerous imports
        dangerous_patterns = [
            "import os", "from os", "__import__", "eval(", "exec(",
            "subprocess", "system(", "open(", "file(", "input(",
            "raw_input(", "compile(", "globals(", "locals(",
        ]
        
        for pattern in dangerous_patterns:
            if pattern in code:
                issues.append(f"Potentially dangerous pattern: {pattern}")
        
        # Check for file operations (if not allowed)
        if not self.constraints.allow_file_writes:
            file_patterns = ["open(", "write(", "w'", 'w"']
            for pattern in file_patterns:
                if pattern in code:
                    issues.append(f"File write operation not allowed: {pattern}")
        
        # Validate imports against allowed list
        import_lines = [line.strip() for line in code.split('\n') 
                       if line.strip().startswith(('import ', 'from '))]
        
        for line in import_lines:
            if line.startswith('import '):
                module = line.split('import ')[1].split()[0].split('.')[0]
            elif line.startswith('from '):
                module = line.split('from ')[1].split()[0].split('.')[0]
            else:
                continue
                
            if module not in self.constraints.allowed_imports:
                issues.append(f"Import not allowed: {module}")
        
        return len(issues) == 0, issues
    
    def prepare_execution_environment(self, code: str) -> Path:
        """
        Prepare temporary file with code for execution.
        
        Args:
            code: Python code to execute
            
        Returns:
            Path to temporary Python file
        """
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(
            mode='w', suffix='.py', delete=False
        )
        
        # Add safety wrapper
        wrapped_code = f"""
import sys
import signal
import resource

# Set memory limit
def set_memory_limit(size_mb):
    try:
        resource.setrlimit(resource.RLIMIT_AS, (size_mb * 1024 * 1024, -1))
    except (ValueError, OSError):
        pass  # Some systems don't support memory limits

# Set execution timeout
def timeout_handler(signum, frame):
    raise TimeoutError("Code execution timed out")

signal.signal(signal.SIGALRM, timeout_handler)
signal.alarm({self.constraints.timeout_seconds})

# Set memory limit if available
set_memory_limit({self.constraints.max_memory_mb})

try:
    # User code execution
{code}
    
except TimeoutError as e:
    print(f"EXECUTION_TIMEOUT: {{e}}", file=sys.stderr)
    sys.exit(124)  # Timeout exit code
except MemoryError as e:
    print(f"MEMORY_LIMIT_EXCEEDED: {{e}}", file=sys.stderr) 
    sys.exit(125)  # Memory limit exit code
except Exception as e:
    print(f"EXECUTION_ERROR: {{type(e).__name__}}: {{e}}", file=sys.stderr)
    sys.exit(1)
finally:
    signal.alarm(0)  # Cancel alarm
"""
        
        temp_file.write(wrapped_code)
        temp_file.flush()
        temp_file.close()
        
        return Path(temp_file.name)
    
    def execute_code(self, code: str, use_subprocess: bool = False) -> SandboxResult:
        """
        Execute Python code in sandbox environment.
        
        Args:
            code: Python code to execute
            use_subprocess: If True, use subprocess execution (more isolation)
                           If False, use direct execution (faster, still restricted)
            
        Returns:
            SandboxResult with execution details
        """
        # Use direct execution by default for better performance and control
        if not use_subprocess:
            return self.execute_code_direct(code)
            
        # Fallback to subprocess execution for maximum isolation
        return self._execute_code_subprocess(code)
    
    def _execute_code_subprocess(self, code: str) -> SandboxResult:
        """Execute code in subprocess for maximum isolation."""
        start_time = time.time()
        
        # Validate code first
        is_valid, issues = self.validate_code(code)
        if not is_valid:
            return SandboxResult(
                success=False,
                stdout="",
                stderr=f"Code validation failed: {'; '.join(issues)}",
                exit_code=126,  # Command cannot execute
                execution_time=0.0,
                status=ProcessingStatus.FAILED,
            )
        
        # Prepare execution environment
        temp_file = self.prepare_execution_environment(code)
        
        try:
            # Execute code in subprocess
            TIMEOUT_EXIT_CODE = 124
            MEMORY_EXIT_CODE = 125
            
            result = subprocess.run(
                ["python", str(temp_file)],
                capture_output=True,
                text=True,
                timeout=self.constraints.timeout_seconds + 5,  # Buffer
                check=False,
            )
            
            execution_time = time.time() - start_time
            
            # Determine status based on exit code
            if result.returncode == 0:
                status = ProcessingStatus.COMPLETED
                success = True
            elif result.returncode == TIMEOUT_EXIT_CODE:
                status = ProcessingStatus.FAILED
                success = False
            elif result.returncode == MEMORY_EXIT_CODE:
                status = ProcessingStatus.FAILED
                success = False
            else:
                status = ProcessingStatus.FAILED
                success = False
            
            # Log outputs if configured
            if self.constraints.log_outputs and result.stdout:
                self.logger.info("Subprocess execution output: %s", result.stdout.strip())
                
            if self.constraints.capture_print_outputs and result.stdout:
                self._captured_outputs.append(result.stdout)
            
            return SandboxResult(
                success=success,
                stdout=result.stdout,
                stderr=result.stderr,
                exit_code=result.returncode,
                execution_time=execution_time,
                status=status,
            )
            
        except subprocess.TimeoutExpired:
            execution_time = time.time() - start_time
            return SandboxResult(
                success=False,
                stdout="",
                stderr="Code execution timed out (process level)",
                exit_code=124,
                execution_time=execution_time,
                status=ProcessingStatus.FAILED,
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            return SandboxResult(
                success=False,
                stdout="",
                stderr=f"Sandbox execution error: {e}",
                exit_code=127,
                execution_time=execution_time,
                status=ProcessingStatus.FAILED,
            )
            
        finally:
            # Cleanup temporary file
            try:
                temp_file.unlink()
            except OSError:
                pass  # File might already be deleted

    def create_restricted_globals(self) -> dict[str, Any]:
        """Create restricted globals dictionary for safe code execution."""
        restricted_globals = {
            "__builtins__": {
                name: getattr(__builtins__, name)
                for name in self.constraints.allowed_builtins
                if hasattr(__builtins__, name)
            },
            "__name__": "__sandbox__",
            "__doc__": None,
        }
        
        # Add safe modules that are pre-approved
        safe_modules = {
            "json": json,
            "re": importlib.import_module("re"),
            "datetime": importlib.import_module("datetime"),
            "pathlib": importlib.import_module("pathlib"),
        }
        
        for name, module in safe_modules.items():
            if name in self.constraints.allowed_imports:
                restricted_globals[name] = module
                
        return restricted_globals
    
    def execute_code_direct(self, code: str) -> SandboxResult:
        """
        Execute code directly in current process with restrictions.
        
        This is safer and faster than subprocess execution for trusted code.
        """
        start_time = time.time()
        
        # Validate code first
        is_valid, issues = self.validate_code(code)
        if not is_valid:
            return SandboxResult(
                success=False,
                stdout="",
                stderr=f"Code validation failed: {'; '.join(issues)}",
                exit_code=126,
                execution_time=0.0,
                status=ProcessingStatus.FAILED,
            )
        
        # Set up execution environment
        original_recursion_limit = sys.getrecursionlimit()
        sys.setrecursionlimit(self.constraints.max_recursion_depth)
        
        # Install import hook
        import_hook = RestrictedImportHook(set(self.constraints.allowed_imports))
        import_hook.install()
        
        # Capture outputs
        stdout_capture = io.StringIO()
        stderr_capture = io.StringIO()
        
        try:
            # Set up timeout
            def timeout_handler(signum, frame):
                raise TimeoutError("Code execution timed out")
            
            signal.signal(signal.SIGALRM, timeout_handler)
            signal.alarm(self.constraints.timeout_seconds)
            
            # Execute code with restricted globals
            with redirect_stdout(stdout_capture), redirect_stderr(stderr_capture):
                restricted_globals = self.create_restricted_globals()
                restricted_locals = {}
                
                # Compile and execute
                compiled_code = compile(code, "<sandbox>", "exec")
                exec(compiled_code, restricted_globals, restricted_locals)
            
            execution_time = time.time() - start_time
            stdout_content = stdout_capture.getvalue()
            stderr_content = stderr_capture.getvalue()
            
            # Log outputs if configured
            if self.constraints.log_outputs and stdout_content:
                self.logger.info(f"Sandbox execution output: {stdout_content.strip()}")
                
            if self.constraints.capture_print_outputs and stdout_content:
                self._captured_outputs.append(stdout_content)
            
            return SandboxResult(
                success=True,
                stdout=stdout_content,
                stderr=stderr_content,
                exit_code=0,
                execution_time=execution_time,
                status=ProcessingStatus.COMPLETED,
            )
            
        except TimeoutError:
            execution_time = time.time() - start_time
            return SandboxResult(
                success=False,
                stdout=stdout_capture.getvalue(),
                stderr="Code execution timed out",
                exit_code=124,
                execution_time=execution_time,
                status=ProcessingStatus.FAILED,
            )
            
        except MemoryError:
            execution_time = time.time() - start_time
            return SandboxResult(
                success=False,
                stdout=stdout_capture.getvalue(),
                stderr="Memory limit exceeded",
                exit_code=125,
                execution_time=execution_time,
                status=ProcessingStatus.FAILED,
            )
            
        except Exception as e:
            execution_time = time.time() - start_time
            error_msg = f"{type(e).__name__}: {e}"
            stderr_content = stderr_capture.getvalue()
            if stderr_content:
                error_msg = f"{stderr_content}\n{error_msg}"
                
            return SandboxResult(
                success=False,
                stdout=stdout_capture.getvalue(),
                stderr=error_msg,
                exit_code=1,
                execution_time=execution_time,
                status=ProcessingStatus.FAILED,
            )
            
        finally:
            # Cleanup
            signal.alarm(0)
            sys.setrecursionlimit(original_recursion_limit)
            import_hook.uninstall()
    
    def get_captured_outputs(self) -> list[str]:
        """Get all captured print outputs from executions."""
        return self._captured_outputs.copy()
    
    def clear_captured_outputs(self) -> None:
        """Clear captured outputs."""
        self._captured_outputs.clear()
        
    def persist_outputs_to_log(self, log_file: str = "logs/sandbox_outputs.log") -> None:
        """Persist captured outputs to a log file for audit trail."""
        if not self._captured_outputs:
            return
            
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        with log_path.open("a", encoding="utf-8") as f:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"\n=== Sandbox Execution Outputs - {timestamp} ===\n")
            for i, output in enumerate(self._captured_outputs, 1):
                f.write(f"--- Output {i} ---\n{output}\n")
            f.write("=== End Outputs ===\n\n")
        
        self.logger.info(f"Persisted {len(self._captured_outputs)} outputs to {log_file}")
        self.clear_captured_outputs()


def create_default_sandbox() -> SandboxRunner:
    """Create sandbox runner with default constraints for tool execution."""
    constraints = SandboxConstraints(
        timeout_seconds=30,
        max_memory_mb=512,
        max_cpu_seconds=15,
        max_recursion_depth=100,
        allow_file_writes=False,
        log_outputs=True,
        capture_print_outputs=True,
    )
    return SandboxRunner(constraints)


def create_mcp_tool_sandbox() -> SandboxRunner:
    """Create sandbox runner optimized for MCP tool execution."""
    constraints = SandboxConstraints(
        timeout_seconds=45,
        max_memory_mb=256,
        max_cpu_seconds=20,
        max_recursion_depth=50,
        allow_file_writes=True,
        output_directory="/workspace/data/output",
        allowed_imports=[
            # Core Python modules
            "json", "re", "datetime", "pathlib", "typing", "dataclasses",
            "collections", "itertools", "functools", "operator", "uuid",
            # MCP server modules only
            "mcp_servers", "mcp_servers.intake", "mcp_servers.analysis",
            "mcp_servers.generation", "mcp_servers.skills",
        ],
        log_outputs=True,
        capture_print_outputs=True,
    )
    return SandboxRunner(constraints)


def create_permissive_sandbox() -> SandboxRunner:
    """Create sandbox runner with more permissive settings for development."""
    constraints = SandboxConstraints(
        timeout_seconds=60,
        max_memory_mb=1024,
        max_cpu_seconds=45,
        max_recursion_depth=200,
        allow_file_writes=True,
        allowed_imports=[
            # Extended stdlib
            "json", "re", "datetime", "pathlib", "typing", "dataclasses",
            "collections", "itertools", "functools", "operator", "uuid",
            "csv", "xml", "html", "urllib", "email", "calendar",
            # MCP modules
            "mcp_servers", "mcp_servers.intake", "mcp_servers.analysis",
            "mcp_servers.generation", "mcp_servers.skills",
        ],
        log_outputs=True,
        capture_print_outputs=True,
    )
    return SandboxRunner(constraints)
