"""
Test suite for OrchestratorController functionality.

This module provides comprehensive testing for the static orchestrator
controller without requiring LLM integration.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Set up path for imports
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from orchestrator.loop import OrchestratorController


class TestOrchestratorController:
    """Test cases for OrchestratorController class."""
    
    def setup_method(self):
        """Setup test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.config_data = {
            "memory": {"default_ttl": 7200},
            "sandbox": {
                "timeout_seconds": 30,
                "max_memory_mb": 512,
                "allowed_imports": ["json", "datetime", "pathlib"]
            }
        }
        
    def teardown_method(self):
        """Clean up after each test method."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    @patch('orchestrator.loop.Path.cwd')
    def test_controller_initialization(self, mock_cwd):
        """Test controller initialization with proper component setup."""
        mock_cwd.return_value = Path(self.temp_dir)
        
        # Create controller instance
        controller = OrchestratorController()
        
        # Verify basic initialization
        assert controller.config_path == "config/orchestrator_config.yaml"
        assert controller.allowed_write_path == Path(self.temp_dir) / "data" / "output"
        assert len(controller.allowed_read_paths) == 4
        assert controller.executor is not None
        assert controller.tools_interface is not None
        assert controller.memory is not None
        assert controller.logger is not None
        
    def test_search_tools_functionality(self):
        """Test tool search functionality."""
        with patch('orchestrator.loop.Path.cwd') as mock_cwd:
            mock_cwd.return_value = Path(self.temp_dir)
            controller = OrchestratorController()
            
            # Test search for intake tools
            intake_tools = controller.search_tools("intake")
            assert isinstance(intake_tools, list)
            assert len(intake_tools) > 0
            
            # Verify tool structure
            for tool in intake_tools:
                assert "name" in tool
                assert "category" in tool
                assert "description" in tool
                assert "module_path" in tool
                assert "parameters" in tool
                
            # Test search for non-existent tools
            missing_tools = controller.search_tools("nonexistent")
            assert isinstance(missing_tools, list)
            
    def test_file_operations(self):
        """Test file loading and writing operations."""
        with patch('orchestrator.loop.Path.cwd') as mock_cwd:
            mock_cwd.return_value = Path(self.temp_dir)
            controller = OrchestratorController()
            
            # Test file writing
            test_content = "Test file content for orchestrator validation"
            result = controller.write_file("test_output.txt", test_content)
            assert result is True
            
            # Verify file was created
            output_path = controller.allowed_write_path / "test_output.txt"
            assert output_path.exists()
            assert output_path.read_text() == test_content
            
            # Test file loading
            loaded_content = controller.load_file(str(output_path))
            assert loaded_content == test_content
            
    def test_file_security_constraints(self):
        """Test file operation security constraints."""
        with patch('orchestrator.loop.Path.cwd') as mock_cwd:
            mock_cwd.return_value = Path(self.temp_dir)
            controller = OrchestratorController()
            
            # Test loading file outside allowed paths should fail
            with pytest.raises((ValueError, FileNotFoundError)):
                controller.load_file("/etc/passwd")
                
            # Test writing with path traversal should be contained
            result = controller.write_file("../../../malicious.txt", "bad content")
            # Should write to safe location, not traverse directories
            assert result is True
            
            # Verify the file is written safely within output directory
            malicious_path = controller.allowed_write_path / "../../../malicious.txt"
            safe_path = controller.allowed_write_path / "malicious.txt" 
            assert not malicious_path.resolve().exists() or safe_path.exists()
            
    def test_python_execution_basic(self):
        """Test Python code execution functionality."""
        with patch('orchestrator.loop.Path.cwd') as mock_cwd:
            mock_cwd.return_value = Path(self.temp_dir)
            controller = OrchestratorController()
            
            # Test simple code execution
            simple_code = "result = 2 + 2"
            execution_result = controller.execute_python(simple_code)
            
            assert isinstance(execution_result, dict)
            assert "success" in execution_result
            assert "output" in execution_result
            assert "error" in execution_result
            assert "execution_time" in execution_result
            assert "execution_id" in execution_result
            
    def test_workflow_execution_structure(self):
        """Test workflow execution with basic steps."""
        with patch('orchestrator.loop.Path.cwd') as mock_cwd:
            mock_cwd.return_value = Path(self.temp_dir)
            controller = OrchestratorController()
            
            # Create simple workflow steps
            workflow_steps = [
                {
                    "name": "test_step_1",
                    "type": "python_execution",
                    "code": "print('Step 1 executed')",
                    "critical": False
                },
                {
                    "name": "test_step_2", 
                    "type": "write_output",
                    "template": "test_output.txt",
                    "data_sources": [],
                    "critical": False
                }
            ]
            
            # Execute workflow
            result = controller.run_reasoning_loop(workflow_steps)
            
            # Verify workflow result structure
            assert isinstance(result, dict)
            assert "workflow_id" in result
            assert "steps_executed" in result
            assert "outputs_generated" in result
            assert "execution_stats" in result
            assert "success" in result
            assert "error_log" in result
            
            # Verify steps were processed
            assert len(result["steps_executed"]) == len(workflow_steps)
            
    def test_default_workflow_steps(self):
        """Test default workflow step generation."""
        with patch('orchestrator.loop.Path.cwd') as mock_cwd:
            mock_cwd.return_value = Path(self.temp_dir)
            controller = OrchestratorController()
            
            # Get default workflow steps
            default_steps = controller._get_default_workflow_steps()
            
            assert isinstance(default_steps, list)
            assert len(default_steps) > 0
            
            # Verify step structure
            for step in default_steps:
                assert "name" in step
                assert "type" in step
                assert "critical" in step
                
    def test_memory_operations(self):
        """Test memory storage and retrieval."""
        with patch('orchestrator.loop.Path.cwd') as mock_cwd:
            mock_cwd.return_value = Path(self.temp_dir)
            controller = OrchestratorController()
            
            # Test memory storage
            test_data = {"test_key": "test_value", "number": 42}
            controller.memory.store("test_item", test_data)
            
            # Test memory retrieval
            retrieved_data = controller.memory.get("test_item")
            assert retrieved_data == test_data
            
            # Test non-existent item
            missing_data = controller.memory.get("non_existent")
            assert missing_data is None
            
    def test_cleanup_resources(self):
        """Test resource cleanup functionality."""
        with patch('orchestrator.loop.Path.cwd') as mock_cwd:
            mock_cwd.return_value = Path(self.temp_dir)
            controller = OrchestratorController()
            
            # Mock executor cleanup to verify it's called
            controller.executor.cleanup_resources = MagicMock()
            
            # Call cleanup
            controller.cleanup_resources()
            
            # Verify executor cleanup was called
            controller.executor.cleanup_resources.assert_called_once()
            
    def test_configuration_loading(self):
        """Test configuration loading from YAML file."""
        with patch('orchestrator.loop.Path.cwd') as mock_cwd:
            mock_cwd.return_value = Path(self.temp_dir)
            
            # Test with missing config file (should use defaults)
            controller = OrchestratorController(config_path="nonexistent.yaml")
            assert controller.config == {}
            
    def test_sandbox_constraints_creation(self):
        """Test sandbox constraints creation from configuration."""
        with patch('orchestrator.loop.Path.cwd') as mock_cwd:
            mock_cwd.return_value = Path(self.temp_dir)
            controller = OrchestratorController()
            
            # Create sandbox constraints
            constraints = controller._create_sandbox_constraints()
            
            # Verify constraint object
            assert hasattr(constraints, 'timeout_seconds')
            assert hasattr(constraints, 'max_memory_mb')
            assert hasattr(constraints, 'allow_file_writes')
            assert hasattr(constraints, 'output_directory')
            assert hasattr(constraints, 'allowed_imports')
            
    @patch('orchestrator.loop.Path.cwd')
    def test_tool_parameter_preparation(self, mock_cwd):
        """Test tool parameter preparation for different tool types."""
        mock_cwd.return_value = Path(self.temp_dir)
        controller = OrchestratorController()
        
        # Test parse_intake tool parameters
        input_data = '{"business_name": "Test Business"}'
        step = {"parameters": {}}
        
        params = controller._prepare_tool_parameters("parse_intake", input_data, step)
        assert "input_data" in params
        assert params["input_data"] == input_data
        
        # Test unknown tool (should return basic parameters)
        params = controller._prepare_tool_parameters("unknown_tool", None, step)
        assert isinstance(params, dict)


def run_orchestrator_tests():
    """Run all orchestrator tests."""
    import subprocess
    
    # Run pytest on this test file
    result = subprocess.run([
        "python", "-m", "pytest", __file__, "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    print("Orchestrator Test Results:")
    print("=" * 50)
    print(result.stdout)
    if result.stderr:
        print("Errors:")
        print(result.stderr)
        
    return result.returncode == 0


if __name__ == "__main__":
    # Run tests when executed directly
    run_orchestrator_tests()
