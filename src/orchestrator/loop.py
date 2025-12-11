"""
High-level orchestration loop for the Client Activation Engine.

This module defines the reasoning loop structure that will coordinate
between different tools and manage the overall workflow state.
"""

import logging
import yaml
import json
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4
from datetime import datetime
import time

from ..core.enums import ProcessingStatus
from ..core.schema_definitions import OrchestrationWorkflow, WorkflowStep
from ..sandbox.sandbox_runner import SandboxRunner, SandboxConstraints
from .executor import SandboxExecutor
from .memory import WorkingMemory, ArtifactRegistry  
from .tools_interface import MCPToolsInterface
from mcp_servers.skills.validators import validate_file_path

logger = logging.getLogger(__name__)


class LoopState(Enum):
    """States in the orchestration reasoning loop."""
    INITIALIZE = auto()
    OBSERVE = auto()
    DECIDE = auto()
    ACT = auto()
    EVALUATE = auto()
    COMPLETE = auto()
    ERROR = auto()


class OrchestrationContext:
    """Context maintained throughout the orchestration process."""
    
    def __init__(self, workflow: OrchestrationWorkflow):
        self.workflow = workflow
        self.current_state = LoopState.INITIALIZE
        self.iteration_count = 0
        self.max_iterations = 50  # From config
        self.observations: dict[str, Any] = {}
        self.decisions: list[str] = []
        self.action_results: dict[str, Any] = {}
        self.error_log: list[str] = []
        
    def add_observation(self, key: str, value: Any) -> None:
        """Add an observation to the context."""
        self.observations[key] = value
        
    def add_decision(self, decision: str) -> None:
        """Record a decision made by the reasoning process."""
        self.decisions.append(decision)
        
    def add_action_result(self, action_name: str, result: Any) -> None:
        """Record the result of an action."""
        self.action_results[action_name] = result
        
    def log_error(self, error: str) -> None:
        """Log an error that occurred during processing."""
        self.error_log.append(error)
        self.workflow.error_log.append(error)


class OrchestrationLoop:
    """
    Main orchestration reasoning loop.
    
    This class implements a high-level reasoning loop that coordinates
    between observation, decision-making, and action execution phases.
    The loop continues until the workflow is complete or an error occurs.
    """
    
    def __init__(self):
        """Initialize the orchestration loop."""
        # These will be injected when the loop is properly implemented
        self.tool_interface = None  # Will reference tools_interface
        self.executor = None        # Will reference executor interface
        self.memory = None          # Will reference memory management
        
    async def run_workflow(self, workflow: OrchestrationWorkflow) -> OrchestrationWorkflow:
        """
        Execute a complete orchestration workflow.
        
        Args:
            workflow: The workflow definition to execute
            
        Returns:
            Updated workflow with execution results
        """
        context = OrchestrationContext(workflow)
        
        try:
            # Initialize workflow
            context.current_state = LoopState.INITIALIZE
            await self._initialize_workflow(context)
            
            # Main reasoning loop
            while (context.current_state != LoopState.COMPLETE and 
                   context.current_state != LoopState.ERROR and
                   context.iteration_count < context.max_iterations):
                
                context.iteration_count += 1
                
                # Execute current state
                if context.current_state == LoopState.OBSERVE:
                    await self._observe_phase(context)
                elif context.current_state == LoopState.DECIDE:
                    await self._decide_phase(context)
                elif context.current_state == LoopState.ACT:
                    await self._act_phase(context)
                elif context.current_state == LoopState.EVALUATE:
                    await self._evaluate_phase(context)
                    
            # Finalize workflow
            await self._finalize_workflow(context)
            
        except Exception as e:
            context.log_error(f"Orchestration loop error: {e}")
            context.current_state = LoopState.ERROR
            workflow.status = ProcessingStatus.FAILED
            
        return context.workflow
    
    async def _initialize_workflow(self, context: OrchestrationContext) -> None:
        """
        Initialize the workflow execution environment.
        
        Args:
            context: Orchestration context
        """
        # Set workflow status
        context.workflow.status = ProcessingStatus.IN_PROGRESS
        
        # Initialize step tracking
        context.workflow.current_step = 0
        
        # Transition to observation phase
        context.current_state = LoopState.OBSERVE
        
    async def _observe_phase(self, context: OrchestrationContext) -> None:
        """
        Observation phase: gather current state and available information.
        
        Args:
            context: Orchestration context
        """
        # TODO: Implement observation logic
        # - Check current workflow step
        # - Gather available data
        # - Assess tool status
        # - Update observations
        
        # Placeholder: Add basic observations
        current_step = context.workflow.current_step or 0
        total_steps = len(context.workflow.steps)
        
        context.add_observation("current_step", current_step)
        context.add_observation("total_steps", total_steps)
        context.add_observation("workflow_progress", current_step / max(total_steps, 1))
        
        # Transition to decision phase
        context.current_state = LoopState.DECIDE
        
    async def _decide_phase(self, context: OrchestrationContext) -> None:
        """
        Decision phase: determine what action to take next.
        
        Args:
            context: Orchestration context
        """
        # TODO: Implement decision logic
        # - Analyze current observations
        # - Determine next best action
        # - Select appropriate tools
        # - Plan execution strategy
        
        # Placeholder: Simple step progression logic
        current_step = context.observations.get("current_step", 0)
        total_steps = context.observations.get("total_steps", 0)
        
        if current_step >= total_steps:
            context.add_decision("workflow_complete")
            context.current_state = LoopState.COMPLETE
        else:
            step = context.workflow.steps[current_step]
            context.add_decision(f"execute_step_{step.name}")
            context.current_state = LoopState.ACT
            
    async def _act_phase(self, context: OrchestrationContext) -> None:
        """
        Action phase: execute the decided actions.
        
        Args:
            context: Orchestration context
        """
        # TODO: Implement action execution
        # - Execute selected tools
        # - Run code in sandbox if needed
        # - Handle tool interactions
        # - Capture results
        
        # Placeholder: Mock step execution
        current_step = context.observations.get("current_step", 0)
        if current_step < len(context.workflow.steps):
            step = context.workflow.steps[current_step]
            
            # Mock execution
            context.add_action_result(step.name, {
                "status": "completed",
                "tool": step.tool,
                "execution_time": 1.0,
            })
            
            # Update workflow progress
            context.workflow.current_step = current_step + 1
            
        # Transition to evaluation phase
        context.current_state = LoopState.EVALUATE
        
    async def _evaluate_phase(self, context: OrchestrationContext) -> None:
        """
        Evaluation phase: assess results and determine next iteration.
        
        Args:
            context: Orchestration context
        """
        # TODO: Implement evaluation logic
        # - Assess action results
        # - Check for errors or issues
        # - Determine if goals are met
        # - Plan next iteration or completion
        
        # Placeholder: Simple progress check
        current_step = context.workflow.current_step or 0
        total_steps = len(context.workflow.steps)
        
        if current_step >= total_steps:
            context.current_state = LoopState.COMPLETE
        else:
            # Continue to next iteration
            context.current_state = LoopState.OBSERVE
            
    async def _finalize_workflow(self, context: OrchestrationContext) -> None:
        """
        Finalize the workflow execution.
        
        Args:
            context: Orchestration context
        """
        # Set final status based on completion state
        if context.current_state == LoopState.COMPLETE:
            context.workflow.status = ProcessingStatus.COMPLETED
        elif context.current_state == LoopState.ERROR:
            context.workflow.status = ProcessingStatus.FAILED
        else:
            context.workflow.status = ProcessingStatus.PAUSED
            
        # Store final results
        context.workflow.results = {
            "total_iterations": context.iteration_count,
            "final_state": context.current_state.name,
            "observations": context.observations,
            "decisions": context.decisions,
            "action_results": context.action_results,
        }


def create_orchestration_loop() -> OrchestrationLoop:
    """
    Create a new orchestration loop instance.
    
    Returns:
        Configured OrchestrationLoop instance
    """
    return OrchestrationLoop()


class OrchestratorController:
    """
    Deterministic orchestrator controller for static workflow execution.
    
    This controller provides lifecycle methods for running predefined workflows
    without LLM dependencies, focusing on file operations, tool execution,
    and sandbox-based Python code execution.
    """
    
    def __init__(self, config_path: str = None):
        """
        Initialize the orchestrator controller.
        
        Args:
            config_path: Path to orchestrator configuration YAML file
        """
        self.config_path = config_path or "config/orchestrator_config.yaml"
        self.config = self._load_config()
        
        # File operation constraints - must be set before creating executor
        self.allowed_read_paths = [
            Path.cwd(),  # Project root
            Path.cwd() / "data",
            Path.cwd() / "tests" / "fixtures",
            Path.cwd() / "config",
        ]
        self.allowed_write_path = Path.cwd() / "data" / "output"
        
        # Ensure output directory exists
        self.allowed_write_path.mkdir(parents=True, exist_ok=True)
        
        # Initialize core components
        self.executor = SandboxExecutor(self._create_sandbox_constraints())
        self.tools_interface = MCPToolsInterface()
        self.memory = WorkingMemory(
            max_items=1000,
            default_ttl=self.config.get("memory", {}).get("default_ttl", 3600),
        )
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        
    def run_reasoning_loop(self, workflow_steps: list[dict] = None) -> dict:
        """
        Execute deterministic workflow with predefined steps.
        
        Args:
            workflow_steps: List of workflow step definitions, if None uses default static workflow
            
        Returns:
            Dictionary containing workflow execution results
        """
        if workflow_steps is None:
            workflow_steps = self._get_default_workflow_steps()
            
        results = {
            "workflow_id": str(uuid4()),
            "steps_executed": [],
            "outputs_generated": [],
            "execution_stats": {},
            "success": True,
            "error_log": []
        }
        
        self.logger.info(f"Starting reasoning loop with {len(workflow_steps)} steps")
        
        try:
            for i, step in enumerate(workflow_steps):
                step_name = step.get("name", f"step_{i}")
                step_type = step.get("type", "unknown")
                
                self.logger.info(f"Executing step {i+1}/{len(workflow_steps)}: {step_name}")
                
                # Update memory with current state
                self.memory.store(f"current_step", step_name)
                self.memory.store(f"step_{i}_started", datetime.utcnow().isoformat())
                
                # Execute step based on type
                step_result = self._execute_workflow_step(step)
                
                # Store results
                results["steps_executed"].append({
                    "step_name": step_name,
                    "step_type": step_type,
                    "success": step_result.get("success", False),
                    "outputs": step_result.get("outputs", []),
                    "execution_time": step_result.get("execution_time", 0)
                })
                
                # Add outputs to global list
                results["outputs_generated"].extend(step_result.get("outputs", []))
                
                # Log step completion
                self.memory.store(f"step_{i}_completed", datetime.utcnow().isoformat())
                
                if not step_result.get("success", False):
                    error_msg = f"Step {step_name} failed: {step_result.get('error', 'Unknown error')}"
                    results["error_log"].append(error_msg)
                    self.logger.error(error_msg)
                    # Continue execution for other steps unless critical failure
                    if step.get("critical", False):
                        results["success"] = False
                        break
                        
        except Exception as e:
            results["success"] = False
            error_msg = f"Workflow execution failed: {str(e)}"
            results["error_log"].append(error_msg)
            self.logger.error(error_msg, exc_info=True)
            
        # Generate execution statistics
        results["execution_stats"] = {
            "total_steps": len(workflow_steps),
            "successful_steps": sum(1 for step in results["steps_executed"] if step["success"]),
            "total_outputs": len(results["outputs_generated"]),
            "executor_stats": self.executor.get_execution_stats()
        }
        
        self.logger.info(f"Reasoning loop completed. Success: {results['success']}")
        return results
        
    def search_tools(self, query: str) -> list[dict]:
        """
        Search available MCP tools by name, category, or description.
        
        Args:
            query: Search query string
            
        Returns:
            List of lightweight tool metadata dictionaries
        """
        self.logger.info(f"Searching tools with query: {query}")
        
        try:
            # Discover all available tools
            tools = self.tools_interface.discover_tools()
            
            # Filter tools based on query
            matching_tools = []
            query_lower = query.lower()
            
            for tool in tools:
                # Check if query matches tool name, category, or description
                if (query_lower in tool.name.lower() or 
                    query_lower in tool.category.value.lower() or
                    query_lower in tool.description.lower()):
                    
                    matching_tools.append({
                        "name": tool.name,
                        "category": tool.category.value,
                        "description": tool.description,
                        "module_path": tool.module_path,
                        "parameters": list(tool.parameters.keys()) if tool.parameters else []
                    })
                    
            self.logger.info(f"Found {len(matching_tools)} matching tools")
            return matching_tools
            
        except Exception as e:
            self.logger.error(f"Tool search failed: {str(e)}")
            return []
            
    def load_file(self, path: str) -> str:
        """
        Load file with validation and logging.
        
        Args:
            path: File path to read (relative to project root or absolute within allowed paths)
            
        Returns:
            File content as string
            
        Raises:
            ValueError: If path is not allowed
            FileNotFoundError: If file doesn't exist
        """
        file_path = Path(path)
        
        # Convert relative paths to absolute
        if not file_path.is_absolute():
            file_path = Path.cwd() / file_path
            
        # Validate file path security
        if not validate_file_path(str(file_path)):
            raise ValueError(f"Invalid file path: {path}")
            
        # Check if path is within allowed read directories
        allowed = any(
            str(file_path).startswith(str(allowed_path))
            for allowed_path in self.allowed_read_paths
        )
        
        if not allowed:
            raise ValueError(f"File path not in allowed directories: {path}")
            
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")
            
        self.logger.info(f"Loading file: {file_path}")
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Normalize line endings
            content = content.replace('\r\n', '\n').replace('\r', '\n')
            
            # Log file operation
            self.memory.store(f"file_read_{file_path.name}", {
                "path": str(file_path),
                "size_bytes": len(content),
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return content
            
        except Exception as e:
            self.logger.error(f"Failed to read file {file_path}: {str(e)}")
            raise
            
    def write_file(self, path: str, content: str) -> bool:
        """
        Write file with directory creation and logging.
        
        Args:
            path: File path to write (relative to output directory)
            content: Content to write
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Resolve path relative to allowed write directory
            file_path = self.allowed_write_path / path
            
            # Ensure parent directories exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"Writing file: {file_path}")
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
                
            # Calculate content hash for audit trail
            import hashlib
            content_hash = hashlib.sha256(content.encode()).hexdigest()
            
            # Log file operation
            self.memory.store(f"file_written_{file_path.name}", {
                "path": str(file_path),
                "size_bytes": len(content),
                "content_hash": content_hash,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            self.logger.info(f"Successfully wrote {len(content)} bytes to {file_path}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to write file {path}: {str(e)}")
            return False
            
    def execute_python(self, code: str, context: dict = None) -> dict:
        """
        Execute Python code in sandbox with logging and audit.
        
        Args:
            code: Python code to execute
            context: Optional execution context variables
            
        Returns:
            Dictionary with execution results
        """
        self.logger.info(f"Executing Python code ({len(code)} characters)")
        
        try:
            # Execute in sandbox
            result = self.executor.submit_code(code, context)
            
            # Log execution for audit trail
            execution_log = {
                "code_length": len(code),
                "success": result.success,
                "execution_time": result.execution_time,
                "output_length": len(result.output) if result.output else 0,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            if result.error:
                execution_log["error"] = result.error
                
            self.memory.store(f"python_execution_{result.execution_id}", execution_log)
            
            return {
                "success": result.success,
                "output": result.output,
                "error": result.error,
                "execution_time": result.execution_time,
                "execution_id": result.execution_id
            }
            
        except Exception as e:
            self.logger.error(f"Python execution failed: {str(e)}")
            return {
                "success": False,
                "output": "",
                "error": str(e),
                "execution_time": 0,
                "execution_id": None
            }
            
    def cleanup_resources(self) -> None:
        """Clean up orchestrator resources."""
        self.logger.info("Cleaning up orchestrator resources")
        
        if self.executor:
            self.executor.cleanup_resources()
            
        if self.memory:
            # Memory cleanup handled by working memory TTL
            pass
            
    def _load_config(self) -> dict:
        """Load configuration from YAML file."""
        try:
            config_path = Path(self.config_path)
            if config_path.exists():
                with open(config_path, 'r') as f:
                    import yaml
                    return yaml.safe_load(f)
            else:
                self.logger.warning(f"Config file not found: {self.config_path}, using defaults")
                return {}
        except Exception as e:
            self.logger.error(f"Failed to load config: {str(e)}")
            return {}
            
    def _create_sandbox_constraints(self) -> SandboxConstraints:
        """Create sandbox constraints from configuration."""
        sandbox_config = self.config.get("sandbox", {})
        
        return SandboxConstraints(
            timeout_seconds=sandbox_config.get("timeout_seconds", 60),
            max_memory_mb=sandbox_config.get("max_memory_mb", 1024),
            allow_file_writes=True,
            output_directory=str(self.allowed_write_path),
            allowed_imports=sandbox_config.get("allowed_imports", [
                "pandas", "numpy", "matplotlib", "json", "csv", "datetime", "pathlib"
            ])
        )
        
    def _get_default_workflow_steps(self) -> list[dict]:
        """Get default static workflow steps for testing."""
        return [
            {
                "name": "load_sample_intake",
                "type": "load_fixture",
                "source": "tests/fixtures/intake_samples/sample_intake_1.json",
                "critical": True
            },
            {
                "name": "parse_intake_data",
                "type": "tool_execution",
                "tool": "parse_intake",
                "input_source": "load_sample_intake",
                "critical": True
            },
            {
                "name": "expand_requirements",
                "type": "tool_execution", 
                "tool": "expand_requirements",
                "input_source": "parse_intake_data",
                "critical": True
            },
            {
                "name": "detect_missing_items",
                "type": "tool_execution",
                "tool": "detect_missing",
                "input_source": "expand_requirements",
                "critical": False
            },
            {
                "name": "generate_lovable_spec",
                "type": "tool_execution",
                "tool": "generate_lovable_spec", 
                "input_source": "expand_requirements",
                "critical": False
            },
            {
                "name": "generate_project_summary",
                "type": "tool_execution",
                "tool": "generate_summary",
                "input_source": "expand_requirements",
                "critical": False
            },
            {
                "name": "write_summary_report",
                "type": "write_output",
                "template": "workflow_summary.md",
                "data_sources": ["parse_intake_data", "expand_requirements", "generate_project_summary"],
                "critical": False
            }
        ]
        
    def _execute_workflow_step(self, step: dict) -> dict:
        """Execute a single workflow step based on its type."""
        step_type = step.get("type")
        step_name = step.get("name", "unnamed_step")
        
        start_time = time.time()
        
        try:
            if step_type == "load_fixture":
                return self._execute_load_fixture_step(step)
            elif step_type == "tool_execution":
                return self._execute_tool_step(step)
            elif step_type == "write_output":
                return self._execute_write_output_step(step)
            elif step_type == "python_execution":
                return self._execute_python_step(step)
            else:
                return {
                    "success": False,
                    "error": f"Unknown step type: {step_type}",
                    "outputs": [],
                    "execution_time": time.time() - start_time
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Step execution failed: {str(e)}",
                "outputs": [],
                "execution_time": time.time() - start_time
            }
            
    def _execute_load_fixture_step(self, step: dict) -> dict:
        """Execute a load fixture step."""
        source_path = step.get("source")
        start_time = time.time()
        
        if not source_path:
            return {
                "success": False,
                "error": "No source path specified for load_fixture step",
                "outputs": [],
                "execution_time": time.time() - start_time
            }
            
        try:
            content = self.load_file(source_path)
            step_name = step.get("name", "fixture_data")
            
            # Store loaded data in memory for use by subsequent steps
            self.memory.store(step_name, content)
            
            return {
                "success": True,
                "outputs": [f"Loaded fixture from {source_path}"],
                "execution_time": time.time() - start_time,
                "data": content
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to load fixture: {str(e)}",
                "outputs": [],
                "execution_time": time.time() - start_time
            }
            
    def _execute_tool_step(self, step: dict) -> dict:
        """Execute a tool execution step."""
        tool_name = step.get("tool")
        input_source = step.get("input_source")
        start_time = time.time()
        
        if not tool_name:
            return {
                "success": False,
                "error": "No tool specified for tool_execution step",
                "outputs": [],
                "execution_time": time.time() - start_time
            }
            
        try:
            # Get input data from memory if specified
            input_data = None
            if input_source:
                input_data = self.memory.get(input_source)
                if input_data is None:
                    return {
                        "success": False,
                        "error": f"Input source '{input_source}' not found in memory",
                        "outputs": [],
                        "execution_time": time.time() - start_time
                    }
                    
            # Prepare tool parameters based on input data
            parameters = self._prepare_tool_parameters(tool_name, input_data, step)
            
            # Execute tool
            result = self.tools_interface.execute_tool(tool_name, parameters)
            
            # Store result in memory for use by subsequent steps
            step_name = step.get("name")
            if step_name:
                self.memory.store(step_name, result)
                
            return {
                "success": True,
                "outputs": [f"Executed tool {tool_name}"],
                "execution_time": time.time() - start_time,
                "tool_result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Tool execution failed: {str(e)}",
                "outputs": [],
                "execution_time": time.time() - start_time
            }
            
    def _execute_write_output_step(self, step: dict) -> dict:
        """Execute a write output step."""
        template_name = step.get("template", "output.txt")
        data_sources = step.get("data_sources", [])
        start_time = time.time()
        
        try:
            # Gather data from specified sources
            collected_data = {}
            for source in data_sources:
                data = self.memory.get(source)
                if data:
                    collected_data[source] = data
                    
            # Generate output content
            output_content = self._generate_output_content(template_name, collected_data)
            
            # Write output file
            output_path = f"static_demo/{template_name}"
            success = self.write_file(output_path, output_content)
            
            if success:
                return {
                    "success": True,
                    "outputs": [f"Generated output file: {output_path}"],
                    "execution_time": time.time() - start_time,
                    "file_path": output_path
                }
            else:
                return {
                    "success": False,
                    "error": "Failed to write output file",
                    "outputs": [],
                    "execution_time": time.time() - start_time
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": f"Write output failed: {str(e)}",
                "outputs": [],
                "execution_time": time.time() - start_time
            }
            
    def _execute_python_step(self, step: dict) -> dict:
        """Execute a Python code step."""
        code = step.get("code", "")
        context = step.get("context", {})
        start_time = time.time()
        
        if not code:
            return {
                "success": False,
                "error": "No code specified for python_execution step",
                "outputs": [],
                "execution_time": time.time() - start_time
            }
            
        try:
            # Inject memory entries into context based on step configuration
            enhanced_context = context.copy()
            
            # Check for input_source or memory_keys in step definition
            input_source = step.get("input_source")
            memory_keys = step.get("memory_keys", [])
            
            if input_source:
                # Load data from memory using input_source
                memory_data = self.memory.get(input_source)
                if memory_data is not None:
                    # Make the data available as 'loaded_content' variable
                    enhanced_context["loaded_content"] = memory_data
                    
            # Load additional memory keys if specified
            for key in memory_keys:
                memory_data = self.memory.get(key)
                if memory_data is not None:
                    enhanced_context[key] = memory_data
                    
            # Also provide access to all previous step outputs (for convenience)
            if hasattr(self, '_current_workflow_memory'):
                for mem_key, mem_value in self._current_workflow_memory.items():
                    if mem_key not in enhanced_context:
                        enhanced_context[mem_key] = mem_value
            
            result = self.execute_python(code, enhanced_context)
            
            outputs = []
            if result["success"]:
                outputs.append("Python code executed successfully")
                if result["output"]:
                    outputs.append(f"Output: {result['output'][:100]}...")
            else:
                outputs.append(f"Python execution failed: {result['error']}")
                
            return {
                "success": result["success"],
                "outputs": outputs,
                "execution_time": time.time() - start_time,
                "python_result": result
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": f"Python step execution failed: {str(e)}",
                "outputs": [],
                "execution_time": time.time() - start_time
            }
            
    def _prepare_tool_parameters(self, tool_name: str, input_data: Any, step: dict) -> dict:
        """Prepare parameters for tool execution based on tool type and input data."""
        parameters = step.get("parameters", {})
        
        # Tool-specific parameter preparation
        if tool_name == "parse_intake":
            if isinstance(input_data, str):
                parameters["input_data"] = input_data
            parameters.setdefault("source_type", "auto_detect")
            parameters.setdefault("client_tier", "business")
            
        elif tool_name == "expand_requirements":
            if input_data and "intake_data" in input_data:
                intake_data = input_data["intake_data"]
                parameters["requirements"] = intake_data.get("requirements", [])
                parameters["business_type"] = intake_data.get("business_type", "general")
                parameters.setdefault("client_tier", "business")
                
        elif tool_name == "detect_missing":
            if input_data and "expanded_requirements" in input_data:
                parameters["requirements"] = input_data["expanded_requirements"]
                parameters.setdefault("current_assets", [])
                parameters.setdefault("scope_level", "standard")
                
        elif tool_name == "generate_lovable_spec":
            if input_data and "expanded_requirements" in input_data:
                parameters["requirements"] = {"expanded": input_data["expanded_requirements"]}
                parameters.setdefault("business_context", {"business_type": "general"})
                
        elif tool_name == "generate_summary":
            if input_data:
                parameters["project_data"] = {
                    "requirements": input_data.get("expanded_requirements", []),
                    "complexity": input_data.get("estimated_complexity", "medium"),
                    "timeline": "standard"
                }
                
        return parameters
        
    def _generate_output_content(self, template_name: str, data: dict) -> str:
        """Generate output content based on template and data."""
        if template_name == "workflow_summary.md":
            return self._generate_workflow_summary(data)
        else:
            # Generic JSON output for unknown templates
            return json.dumps(data, indent=2, default=str)
            
    def _generate_workflow_summary(self, data: dict) -> str:
        """Generate a markdown summary of the workflow execution."""
        summary_lines = [
            "# Client Activation Engine - Workflow Summary",
            "",
            f"Generated on: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')} UTC",
            "",
            "## Workflow Execution Results",
            ""
        ]
        
        # Add data from each source
        for source_name, source_data in data.items():
            summary_lines.extend([
                f"### {source_name.replace('_', ' ').title()}",
                "",
                f"```json",
                json.dumps(source_data, indent=2, default=str)[:1000] + "...",
                "```",
                ""
            ])
            
        return "\n".join(summary_lines)
