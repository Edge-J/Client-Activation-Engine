#!/usr/bin/env python3
"""Simple test script for the critical fixes."""

import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
sys.path.insert(0, str(Path(__file__).parent.parent))

def main():
    print("🚀 Testing Critical Fixes")
    print("=" * 40)
    
    # Test 1: Memory get() method
    try:
        from orchestrator.memory import WorkingMemory
        memory = WorkingMemory()
        memory.store("test", "value")
        result = memory.get("test")
        if result == "value":
            print("✅ Fix 1: WorkingMemory.get() method works")
        else:
            print("❌ Fix 1: WorkingMemory.get() failed")
            return False
    except Exception as e:
        print(f"❌ Fix 1: WorkingMemory error - {e}")
        return False
    
    # Test 2: Tool module paths
    try:
        from orchestrator.tools_interface import MCPToolsInterface
        interface = MCPToolsInterface()
        tools = interface.discover_tools()
        
        # Check if we have tools and their module paths are correct
        if tools:
            sample_tool = tools[0]
            if sample_tool.module_path.startswith("mcp_servers."):
                print(f"✅ Fix 2: Tool module paths correct (example: {sample_tool.module_path})")
            else:
                print(f"❌ Fix 2: Tool module path wrong format: {sample_tool.module_path}")
                return False
        else:
            print("❌ Fix 2: No tools discovered")
            return False
    except Exception as e:
        print(f"❌ Fix 2: Tool discovery error - {e}")
        return False
    
    print("\n🎉 Both critical fixes are working!")
    print("Phase 2 blockers resolved!")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
