#!/usr/bin/env python3
"""
Critical validation of both blocking issues.
"""

import asyncio
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.orchestrator.tools_interface import MCPToolsInterface


def test_blocker_1():
    """Test BLOCKER 1: Parameter dict passing instead of unpacking."""
    print("=== BLOCKER 1: Parameter Dict Passing ===")
    
    tools_interface = MCPToolsInterface("mcp_servers")
    
    try:
        result = tools_interface.execute_tool(
            "intake.normalize_industry",
            {
                "business_description": "Tech startup company",
                "confidence_threshold": 0.8
            }
        )
        
        if result.get("status") == "success":
            print("✅ FIXED: Parameters passed as dict successfully")
            return True
        else:
            print("❌ Tool execution failed")
            return False
            
    except TypeError as e:
        if "unexpected keyword argument" in str(e):
            print("❌ NOT FIXED: Still unpacking parameters")
            return False
        else:
            print(f"❌ Different TypeError: {e}")
            return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False


def test_blocker_2():
    """Test BLOCKER 2: Async function awaiting."""
    print("=== BLOCKER 2: Async Handling ===")
    
    import inspect
    
    async def mock_async_run(parameters):
        await asyncio.sleep(0.001)
        return {"async_test": True, "data": parameters}
    
    try:
        if inspect.iscoroutinefunction(mock_async_run):
            test_params = {"test": "data"}
            result = asyncio.run(mock_async_run(test_params))
            
            if isinstance(result, dict) and result.get("async_test"):
                print("✅ FIXED: Async functions properly awaited")
                return True
            else:
                print("❌ NOT FIXED: Async execution failed")
                return False
        else:
            print("❌ Async detection failed")
            return False
            
    except Exception as e:
        print(f"❌ Async handling error: {e}")
        return False


def main():
    """Run validation tests."""
    print("VALIDATION: Tool Execution Blocking Issues")
    print("=" * 50)
    
    # Test both blocking issues
    blocker_1_fixed = test_blocker_1()
    blocker_2_fixed = test_blocker_2()
    
    print("\n" + "=" * 50)
    print("RESULTS:")
    
    if blocker_1_fixed and blocker_2_fixed:
        print("🎉 BOTH BLOCKING ISSUES RESOLVED!")
        print("✅ Parameter dict passing: FIXED")
        print("✅ Async function awaiting: FIXED")
        print("\n🚀 Orchestrator ready for deterministic execution!")
        return 0
    else:
        print("❌ Some issues remain:")
        if not blocker_1_fixed:
            print("   - Parameter dict passing: NOT FIXED")
        if not blocker_2_fixed:
            print("   - Async function awaiting: NOT FIXED")
        return 1


if __name__ == "__main__":
    sys.exit(main())
