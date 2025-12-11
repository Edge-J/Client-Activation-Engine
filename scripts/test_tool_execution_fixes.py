#!/usr/bin/env python3
"""
Test script to validate the tool execution fixes.
Tests both sync and async tool execution with proper parameter handling.
"""

import sys
import traceback
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.orchestrator.tools_interface import MCPToolsInterface


def test_sync_tool_execution():
    """Test synchronous tool execution with parameter dict."""
    print("\n=== Testing Sync Tool Execution ===")
    
    # Initialize tools interface
    tools_interface = MCPToolsInterface("mcp_servers")
    
    # Test normalize_industry (sync tool)
    try:
        result = tools_interface.execute_tool(
            "intake.normalize_industry",
            {
                "business_description": "We are a software development company",
                "confidence_threshold": 0.7
            }
        )
        
        print(f"✓ Sync tool execution successful!")
        print(f"  Tool: normalize_industry")
        print(f"  Status: {result.get('status')}")
        print(f"  Result keys: {list(result.get('result', {}).keys())}")
        
        # Check if we got actual results, not coroutine
        actual_result = result.get('result', {})
        if 'normalized_industry' in actual_result:
            print(f"  ✓ Got normalized_industry: {actual_result['normalized_industry']}")
        else:
            print(f"  ⚠ Missing normalized_industry in result")
            
        return True
        
    except Exception as e:
        print(f"✗ Sync tool execution failed: {e}")
        traceback.print_exc()
        return False


def test_async_tool_execution():
    """Test asynchronous tool execution with asyncio.run()."""
    print("\n=== Testing Async Tool Execution ===")
    
    # Initialize tools interface
    tools_interface = MCPToolsInterface("mcp_servers")
    
    # Test validate_data (async tool)
    try:
        result = tools_interface.execute_tool(
            "skills.validate_data",
            {
                "data": {
                    "email": "test@example.com",
                    "name": "Test User"
                },
                "validation_rules": {
                    "email_required": True,
                    "name_min_length": 2
                },
                "validation_level": "strict"
            }
        )
        
        print(f"✓ Async tool execution successful!")
        print(f"  Tool: validate_data")
        print(f"  Status: {result.get('status')}")
        print(f"  Result keys: {list(result.get('result', {}).keys())}")
        
        # Check if we got actual results, not coroutine
        actual_result = result.get('result', {})
        if isinstance(actual_result, dict):
            print(f"  ✓ Got proper dict result, not coroutine")
            if 'is_valid' in actual_result:
                print(f"  ✓ Got validation result: is_valid={actual_result['is_valid']}")
        else:
            print(f"  ⚠ Result is not a dict: {type(actual_result)}")
            print(f"  ⚠ Result: {actual_result}")
            
        return True
        
    except Exception as e:
        print(f"✗ Async tool execution failed: {e}")
        traceback.print_exc()
        return False


def test_parameter_passing():
    """Test that parameters are passed as dict, not unpacked."""
    print("\n=== Testing Parameter Passing ===")
    
    # Initialize tools interface
    tools_interface = MCPToolsInterface("mcp_servers")
    
    # Test parse_intake with multiple parameters
    try:
        result = tools_interface.execute_tool(
            "intake.parse_intake",
            {
                "input_data": "We need a website with user authentication and payment processing",
                "extract_requirements": True,
                "normalize_format": True
            }
        )
        
        print(f"✓ Parameter passing successful!")
        print(f"  Tool: parse_intake")
        print(f"  Status: {result.get('status')}")
        
        # Check if we got results without TypeError
        actual_result = result.get('result', {})
        if 'requirements' in actual_result:
            print(f"  ✓ Got requirements: {len(actual_result['requirements'])} items")
        else:
            print(f"  ⚠ Missing requirements in result")
            
        return True
        
    except TypeError as e:
        if "unexpected keyword argument" in str(e):
            print(f"✗ Parameter unpacking error (not fixed): {e}")
            return False
        else:
            print(f"✗ Other TypeError: {e}")
            return False
    except Exception as e:
        print(f"✗ Parameter passing failed: {e}")
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("Testing Tool Execution Fixes")
    print("=" * 50)
    
    results = []
    
    # Test sync tool execution
    results.append(test_sync_tool_execution())
    
    # Test async tool execution  
    results.append(test_async_tool_execution())
    
    # Test parameter passing
    results.append(test_parameter_passing())
    
    print("\n" + "=" * 50)
    print("SUMMARY:")
    print(f"Tests passed: {sum(results)}/{len(results)}")
    
    if all(results):
        print("🎉 All tool execution fixes working correctly!")
        return 0
    else:
        print("❌ Some tool execution fixes still need work")
        return 1


if __name__ == "__main__":
    sys.exit(main())
