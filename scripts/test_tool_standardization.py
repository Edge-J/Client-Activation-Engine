#!/usr/bin/env python3
"""
Test the refactored tools to ensure they work with the standardized interface.
"""

import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "src"))

from src.orchestrator.tools_interface import MCPToolsInterface


def test_generate_code_refactored():
    """Test that generate_code now works with parameter dict."""
    print("=== Testing generate_code (async) ===")
    
    tools_interface = MCPToolsInterface("mcp_servers")
    
    try:
        result = tools_interface.execute_tool(
            "generation.generate_code",
            {
                "requirements": {
                    "functional_requirements": ["user authentication", "data processing"],
                    "technical_requirements": ["RESTful API", "database storage"]
                },
                "asset_type": "code",
                "technology_stack": {
                    "backend": "Python Flask",
                    "database": "PostgreSQL"
                }
            }
        )
        
        if result.get("status") == "success":
            print("✅ generate_code refactored successfully!")
            print(f"   Asset type: {result.get('result', {}).get('asset_type', 'N/A')}")
            return True
        else:
            print(f"❌ Tool execution failed: {result}")
            return False
            
    except TypeError as e:
        if "missing" in str(e) and "positional argument" in str(e):
            print(f"❌ NOT FIXED: Still expects positional args: {e}")
            return False
        else:
            print(f"❌ Different TypeError: {e}")
            return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False


def test_validate_data_refactored():
    """Test that validate_data now works with parameter dict."""
    print("=== Testing validate_data (async) ===")
    
    tools_interface = MCPToolsInterface("mcp_servers")
    
    try:
        result = tools_interface.execute_tool(
            "skills.validate_data", 
            {
                "data": {
                    "email": "user@example.com",
                    "age": 25,
                    "name": "Test User"
                },
                "validation_rules": {
                    "email": {"required": True, "type": "email"},
                    "age": {"required": True, "type": "number", "min": 18},
                    "name": {"required": True, "type": "string", "min_length": 2}
                },
                "validation_level": "moderate"
            }
        )
        
        if result.get("status") == "success":
            print("✅ validate_data refactored successfully!")
            validation_result = result.get("result", {})
            print(f"   Is valid: {validation_result.get('is_valid', 'N/A')}")
            return True
        else:
            print(f"❌ Tool execution failed: {result}")
            return False
            
    except TypeError as e:
        if "missing" in str(e) and "positional argument" in str(e):
            print(f"❌ NOT FIXED: Still expects positional args: {e}")
            return False
        else:
            print(f"❌ Different TypeError: {e}")
            return False
    except Exception as e:
        print(f"❌ Other error: {e}")
        return False


def test_existing_tools_still_work():
    """Test that existing dict-style tools still work."""
    print("=== Testing existing tools (sync) ===")
    
    tools_interface = MCPToolsInterface("mcp_servers")
    
    try:
        result = tools_interface.execute_tool(
            "intake.normalize_industry",
            {
                "business_description": "Software development company",
                "confidence_threshold": 0.7
            }
        )
        
        if result.get("status") == "success":
            print("✅ Existing tools still work!")
            return True
        else:
            print("❌ Existing tools broken")
            return False
            
    except Exception as e:
        print(f"❌ Existing tool error: {e}")
        return False


def main():
    """Test all refactored tools."""
    print("TESTING: Refactored Tool Signatures")
    print("=" * 50)
    
    results = []
    
    # Test the two refactored async tools
    results.append(test_generate_code_refactored())
    results.append(test_validate_data_refactored())
    
    # Test that existing tools still work
    results.append(test_existing_tools_still_work())
    
    print("\n" + "=" * 50)
    print("RESULTS:")
    
    if all(results):
        print("🎉 ALL TOOLS STANDARDIZED!")
        print("✅ generate_code: Fixed to use parameters dict")
        print("✅ validate_data: Fixed to use parameters dict") 
        print("✅ Existing tools: Still working")
        print("\n🚀 Uniform tool interface complete!")
        print("   All tools now use: run(parameters: dict) -> dict")
        return 0
    else:
        print("❌ Some tools still have issues:")
        if not results[0]:
            print("   - generate_code: Still broken")
        if not results[1]:
            print("   - validate_data: Still broken")
        if not results[2]:
            print("   - Existing tools: Broken")
        return 1


if __name__ == "__main__":
    sys.exit(main())
