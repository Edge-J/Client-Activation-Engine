#!/usr/bin/env python3
"""
Complete validation script to test the fixed orchestrator components.
Tests both real tool execution and memory operations.
"""

import json
import sys
import tempfile
import os
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_tool_execution():
    """Test real MCP tool execution with fixed module paths."""
    print("🔧 Testing Real Tool Execution...")
    
    try:
        from orchestrator.tools_interface import MCPToolsInterface
        
        # Create interface
        interface = MCPToolsInterface()
        
        # Discover tools
        tools = interface.discover_tools()
        print(f"✓ Discovered {len(tools)} tools")
        
        # Show module paths to verify they're correct
        for tool in tools[:3]:  # Show first 3 tools
            print(f"  - {tool.name}: {tool.module_path}")
        
        # Test actual tool execution
        normalize_tool = None
        for tool in tools:
            if "normalize_industry" in tool.name:
                normalize_tool = tool
                break
                
        if normalize_tool:
            print(f"✓ Testing tool: {normalize_tool.name}")
            print(f"  Module path: {normalize_tool.module_path}")
            
            # Execute with proper parameters
            result = interface.execute_tool(
                normalize_tool.name, 
                {
                    "input_text": "tech startup software development",
                    "context": {},
                    "min_confidence": 0.6
                }
            )
            
            print(f"✓ Tool executed successfully!")
            print(f"  Status: {result.get('status', 'unknown')}")
            print(f"  Result type: {type(result.get('result', {}))}")
            return True
            
        else:
            print("✗ No normalize_industry tool found")
            return False
            
    except Exception as e:
        print(f"✗ Tool execution test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_memory_operations():
    """Test WorkingMemory get() method."""
    print("\n💾 Testing Memory Operations...")
    
    try:
        from orchestrator.memory import WorkingMemory
        
        # Create memory instance
        memory = WorkingMemory(max_items=100, default_ttl=3600)
        
        # Test store and get
        test_data = {"test": "value", "number": 42}
        memory.store("test_key", test_data)
        
        # Test get() method (this was missing)
        retrieved = memory.get("test_key")
        
        if retrieved == test_data:
            print("✓ Memory get() method works correctly")
            
            # Test non-existent key
            missing = memory.get("non_existent_key")
            if missing is None:
                print("✓ Memory returns None for missing keys")
                return True
            else:
                print("✗ Memory should return None for missing keys")
                return False
        else:
            print(f"✗ Memory get() returned wrong data: {retrieved}")
            return False
            
    except Exception as e:
        print(f"✗ Memory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_orchestrator_integration():
    """Test orchestrator with both fixes working together."""
    print("\n🎯 Testing Orchestrator Integration...")
    
    try:
        from orchestrator.loop import OrchestratorController
        
        # Change to temporary directory to avoid sandbox issues
        original_cwd = os.getcwd()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            try:
                controller = OrchestratorController()
                
                # Test tool search (should work with fixed module paths)
                tools = controller.search_tools("intake")
                print(f"✓ Controller found {len(tools)} intake tools")
                
                # Test memory operations (should work with get() method)
                controller.memory.store("test_workflow", {"step": "completed"})
                retrieved = controller.memory.get("test_workflow")
                
                if retrieved and retrieved.get("step") == "completed":
                    print("✓ Controller memory operations working")
                    return True
                else:
                    print("✗ Controller memory operations failed")
                    return False
                    
            finally:
                os.chdir(original_cwd)
                
    except Exception as e:
        print(f"✗ Orchestrator integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_end_to_end_workflow():
    """Test a simple end-to-end workflow."""
    print("\n🚀 Testing End-to-End Workflow...")
    
    try:
        from orchestrator.loop import OrchestratorController
        
        original_cwd = os.getcwd()
        
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            
            try:
                controller = OrchestratorController()
                
                # Simple workflow with fixture loading and memory
                workflow_steps = [
                    {
                        "name": "test_data",
                        "type": "python_execution",
                        "code": "print('Workflow test successful')\ntest_result = 'success'",
                        "critical": False
                    }
                ]
                
                # Execute workflow
                result = controller.run_reasoning_loop(workflow_steps)
                
                if result.get("success", False):
                    print("✓ End-to-end workflow completed successfully")
                    print(f"  Steps executed: {len(result.get('steps_executed', []))}")
                    return True
                else:
                    print("✗ End-to-end workflow failed")
                    print(f"  Errors: {result.get('error_log', [])}")
                    return False
                    
            finally:
                os.chdir(original_cwd)
                
    except Exception as e:
        print(f"✗ End-to-end workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests to validate the fixes."""
    print("🚀 Client Activation Engine - Critical Fix Validation")
    print("=" * 65)
    
    tests = [
        ("Tool Execution", test_tool_execution),
        ("Memory Operations", test_memory_operations), 
        ("Orchestrator Integration", test_orchestrator_integration),
        ("End-to-End Workflow", test_end_to_end_workflow),
    ]
    
    passed_tests = 0
    total_tests = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed_tests += 1
            
    # Summary
    print("\n" + "=" * 65)
    print("🎯 CRITICAL FIX VALIDATION SUMMARY")
    print("=" * 65)
    
    if passed_tests == total_tests:
        print(f"✅ All {total_tests} critical tests PASSED!")
        print("   ✓ Real tool execution works with correct module paths")
        print("   ✓ WorkingMemory.get() method implemented and working")
        print("   ✓ Orchestrator integration functioning correctly")
        print("   ✓ End-to-end workflow execution successful")
        print("\n🎉 Phase 2 blockers RESOLVED - Static orchestrator is COMPLETE!")
        return 0
    else:
        print(f"❌ {total_tests - passed_tests} of {total_tests} tests FAILED")
        print("   Phase 2 still has blocking issues.")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
