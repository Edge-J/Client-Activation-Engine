"""
Sandbox Runner for secure Python code execution.

This module provides a safe environment for executing dynamically generated
Python code with controlled access to imports and file system operations.
"""

import subprocess
import tempfile
import time
from pathlib import Path
from typing import Any, NamedTuple

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
    """Configuration for sandbox execution limits."""
    
    def __init__(
        self,
        timeout_seconds: int = 30,
        max_memory_mb: int = 512,
        allowed_imports: list[str] | None = None,
        allow_file_writes: bool = False,
        output_directory: str | None = None,
    ):
        self.timeout_seconds = timeout_seconds
        self.max_memory_mb = max_memory_mb
        self.allowed_imports = allowed_imports or [
            "pandas", "numpy", "matplotlib", "seaborn", "plotly", "requests"
        ]
        self.allow_file_writes = allow_file_writes
        self.output_directory = output_directory or "/workspace/data/output"


class SandboxRunner:
    """Secure Python code execution environment."""
    
    def __init__(self, constraints: SandboxConstraints | None = None):
        self.constraints = constraints or SandboxConstraints()
        
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
    
    def execute_code(self, code: str) -> SandboxResult:
        """
        Execute Python code in sandbox environment.
        
        Args:
            code: Python code to execute
            
        Returns:
            SandboxResult with execution details
        """
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
            result = subprocess.run(
                ["python", str(temp_file)],
                capture_output=True,
                text=True,
                timeout=self.constraints.timeout_seconds + 5,  # Buffer
            )
            
            execution_time = time.time() - start_time
            
            # Determine status based on exit code
            if result.returncode == 0:
                status = ProcessingStatus.COMPLETED
                success = True
            elif result.returncode == 124:  # Timeout
                status = ProcessingStatus.FAILED
                success = False
            elif result.returncode == 125:  # Memory limit
                status = ProcessingStatus.FAILED
                success = False
            else:
                status = ProcessingStatus.FAILED
                success = False
            
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


def create_default_sandbox() -> SandboxRunner:
    """Create sandbox runner with default constraints."""
    constraints = SandboxConstraints(
        timeout_seconds=30,
        max_memory_mb=512,
        allow_file_writes=False,
    )
    return SandboxRunner(constraints)


def create_permissive_sandbox() -> SandboxRunner:
    """Create sandbox runner with more permissive settings."""
    constraints = SandboxConstraints(
        timeout_seconds=60,
        max_memory_mb=1024,
        allow_file_writes=True,
        allowed_imports=[
            "pandas", "numpy", "matplotlib", "seaborn", "plotly", 
            "requests", "json", "csv", "datetime", "pathlib",
        ],
    )
    return SandboxRunner(constraints)
