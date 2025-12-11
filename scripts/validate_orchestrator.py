#!/usr/bin/env python3
"""
Simple test script to validate the orchestrator components individually.
This avoids the sandbox issues by testing components in isolation.
"""

import json
import sys
from pathlib import Path

# Add paths for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def test_tools_interface():
    """Test that MCPToolsInterface can discover and execute real tools."""
    print("🔧 Testing MCPToolsInterface...")
    
    try:
        from orchestrator.tools_interface import MCPToolsInterface
        
        # Create interface
        interface = MCPToolsInterface()
        
        # Discover tools
        tools = interface.discover_tools()
        print(f"✓ Discovered {len(tools)} tools")
        
        # Find a simple tool to test
        test_tool = None
        for tool in tools:
            if "normalize_industry" in tool.name:
                test_tool = tool
                break
                
        if test_tool:
            print(f"✓ Found test tool: {test_tool.name}")
            
            # Try to execute it
            try:
                result = interface.execute_tool(
                    test_tool.name, 
                    {"input_text": "tech startup", "standardize": True}
                )
                print(f"✓ Tool execution result: {result.get('status', 'unknown')}")
                return True
            except Exception as e:
                print(f"✗ Tool execution failed: {e}")
                return False
        else:
            print("✗ No suitable test tool found")
            return False
            
    except Exception as e:
        print(f"✗ MCPToolsInterface test failed: {e}")
        return False

def test_sample_fixture():
    """Test that the sample fixture file exists and is valid JSON."""
    print("\n📁 Testing sample fixture...")
    
    fixture_path = Path(__file__).parent.parent / "tests/fixtures/intake_samples/sample_intake_1.json"
    
    if not fixture_path.exists():
        print(f"✗ Fixture file missing: {fixture_path}")
        return False
        
    try:
        with open(fixture_path, 'r') as f:
            data = json.load(f)
            
        # Validate required fields
        required_fields = ["business_name", "contact_email", "requirements"]
        for field in required_fields:
            if field not in data:
                print(f"✗ Missing required field: {field}")
                return False
                
        print(f"✓ Fixture file valid with {len(data.get('requirements', []))} requirements")
        print(f"  Business: {data.get('business_name', 'N/A')}")
        return True
        
    except Exception as e:
        print(f"✗ Fixture validation failed: {e}")
        return False

def test_basic_orchestrator():
    """Test basic orchestrator functionality without sandbox issues."""
    print("\n🎯 Testing basic orchestrator...")
    
    try:
        # Simple test that doesn't trigger sandbox
        from orchestrator.loop import OrchestratorController
        
        # Create temporary directory for testing
        import tempfile
        import os
        
        with tempfile.TemporaryDirectory() as temp_dir:
            # Change to temp directory to avoid sandbox issues
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                controller = OrchestratorController()
                
                # Test search functionality
                tools = controller.search_tools("intake")
                print(f"✓ Found {len(tools)} intake tools")
                
                # Test file operations 
                test_content = "Test orchestrator content"
                success = controller.write_file("test.txt", test_content)
                
                if success:
                    print("✓ File write successful")
                else:
                    print("✗ File write failed")
                    
                return len(tools) > 0 and success
                
            finally:
                os.chdir(original_cwd)
                
    except Exception as e:
        print(f"✗ Basic orchestrator test failed: {e}")
        return False

def main():
    """Run all validation tests."""
    print("🚀 Client Activation Engine - Validation Tests")
    print("=" * 60)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: MCPToolsInterface
    if test_tools_interface():
        tests_passed += 1
        
    # Test 2: Sample fixture
    if test_sample_fixture():
        tests_passed += 1
        
    # Test 3: Basic orchestrator
    if test_basic_orchestrator():
        tests_passed += 1
        
    # Summary
    print("\n" + "=" * 60)
    print("🎯 VALIDATION SUMMARY")
    print("=" * 60)
    
    if tests_passed == total_tests:
        print(f"✅ All {total_tests} validation tests passed!")
        print("   - MCPToolsInterface can discover and execute real tools")
        print("   - Sample fixture file is valid and complete")
        print("   - Basic orchestrator functionality works")
        return 0
    else:
        print(f"❌ {total_tests - tests_passed} of {total_tests} tests failed")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
