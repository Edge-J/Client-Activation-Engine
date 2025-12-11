#!/usr/bin/env python3
"""
Test the core tool execution fixes directly - parameter dict passing and async handling.
Tests both fixes in isolation.
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.orchestrator.tools_interface import MCPToolsInterface


def test_parameter_dict_fix():
    """Test that tools receive parameters as dict, not unpacked kwargs."""
    print("\n=== Testing Parameter Dict Fix ===")
    
    tools_interface = MCPToolsInterface("mcp_servers")
    
    # Test with normalize_industry (sync tool without relative imports)
    try:
        result = tools_interface.execute_tool(
            "intake.normalize_industry",
            {
                "business_description": "We develop mobile applications",
                "confidence_threshold": 0.8,
                "processing_mode": "detailed"
            }
        )
        
        print("✓ Parameter dict fix working!")
        print(f"  Status: {result.get('status')}")
        print(f"  Tool executed without TypeError")
        
        # Verify we got actual results
        tool_result = result.get('result', {})
        if isinstance(tool_result, dict) and 'normalized_industry' in tool_result:
            print(f"  ✓ Got valid result: {tool_result['normalized_industry']}")
            return True
        else:
            print(f"  ⚠ Unexpected result format: {type(tool_result)}")
            return False
            
    except TypeError as e:
        if "unexpected keyword argument" in str(e):
            print(f"✗ Parameter dict fix FAILED - still unpacking: {e}")
            return False
        else:
            print(f"✗ Different TypeError: {e}")
            return False
    except Exception as e:
        print(f"✗ Other error: {e}")
        return False


def test_async_detection():
    """Test that async functions are detected properly."""
    print("\n=== Testing Async Function Detection ===")
    
    tools_interface = MCPToolsInterface("mcp_servers")
    
    # Discover tools first
    tools = tools_interface.discover_tools()
    
    # Check if any async tools are found and how they're handled
    async_tools = []
    sync_tools = []
    
    for tool in tools:
        try:
            # Import and check the function type
            project_root = Path(__file__).parent.parent
            original_cwd = Path.cwd()
            import os
            original_path = sys.path[:]
            
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            os.chdir(str(project_root))
            
            try:
                import importlib
                import inspect
                module = importlib.import_module(tool.module_path)
                
                if hasattr(module, "run"):
                    run_func = getattr(module, "run")
                    if inspect.iscoroutinefunction(run_func):
                        async_tools.append(tool.name)
                    else:
                        sync_tools.append(tool.name)
                        
            finally:
                os.chdir(str(original_cwd))
                sys.path[:] = original_path
                
        except Exception:
            # Skip tools with import issues for this test
            continue
    
    print(f"  Found {len(sync_tools)} sync tools: {sync_tools[:3]}...")
    print(f"  Found {len(async_tools)} async tools: {async_tools}")
    
    if len(async_tools) > 0:
        print("  ✓ Async tools detected - inspection working")
        return True
    else:
        print("  ⚠ No async tools found or detection issue")
        return False


def test_orchestrator_integration():
    """Test that tools work in orchestrator context."""
    print("\n=== Testing Orchestrator Integration ===")
    
    from src.orchestrator.loop import OrchestratorController
    
    try:
        controller = OrchestratorController()
        
        # Test search_tools (should work now with parameter fix)
        tools = controller.search_tools("intake")
        
        print(f"  Found {len(tools)} intake tools")
        
        if len(tools) > 0:
            print("  ✓ Tool search working in orchestrator")
            return True
        else:
            print("  ✗ No tools found")
            return False
            
    except Exception as e:
        print(f"  ✗ Orchestrator integration failed: {e}")
        return False


def main():
    """Run focused tests on the core fixes."""
    print("Testing Core Tool Execution Fixes")
    print("=" * 60)
    
    results = []
    
    # Test 1: Parameter dict fix (most critical)
    results.append(test_parameter_dict_fix())
    
    # Test 2: Async detection (less critical for basic functionality)
    results.append(test_async_detection())
    
    # Test 3: Orchestrator integration (end-to-end verification)
    results.append(test_orchestrator_integration())
    
    print("\n" + "=" * 60)
    print("SUMMARY:")
    print(f"Core fixes working: {sum(results)}/{len(results)}")
    
    # Check most critical fix
    param_fix_working = results[0] if len(results) > 0 else False
    
    if param_fix_working:
        print("✅ CRITICAL FIX CONFIRMED: Parameter dict passing working!")
        print("   Tools can now be executed without TypeError.")
        print("   Orchestrator should be able to execute workflows.")
        
        # If async detection also works, even better
        if len(results) > 1 and results[1]:
            print("✅ BONUS: Async detection also working!")
            
        return 0
    else:
        print("❌ CRITICAL FIX FAILED: Parameter dict issue not resolved")
        return 1


if __name__ == "__main__":
    sys.exit(main())
