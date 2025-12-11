"""
Simplified integration tests for MCP tools.

These tests validate that all MCP tools can be imported and called
with basic parameters, ensuring the foundation is complete.
"""

import os
import pytest
import sys

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from mcp_servers.analysis import extract_assets, detect_missing
from mcp_servers.generation import generate_lovable_spec, generate_tasks, generate_timeline, generate_summary
from mcp_servers.skills import validators, cleaning, text_rules


class TestMCPToolsIntegration:
    """Integration tests for MCP tools foundation."""

    def test_validators_module_available(self):
        """Test that validators module is available with key functions."""
        assert hasattr(validators, 'validate_email')
        assert hasattr(validators, 'validate_phone') 
        assert hasattr(validators, 'validate_business_type')
        assert hasattr(validators, 'validate_confidence_score')
        
        # Test basic validation functions work
        assert validators.validate_email("test@example.com")
        assert not validators.validate_email("invalid-email")
        assert validators.validate_phone("(555) 123-4567")
        assert validators.validate_business_type("healthcare")

    def test_extract_assets_callable(self):
        """Test extract_assets can be called with basic parameters."""
        params = {
            "requirements": {"website": {"confidence": 0.8}},
            "business_context": {"business_type": "consulting"},
            "scope_level": "standard"
        }
        
        result = extract_assets.run(params)
        
        # Should return expected structure
        assert isinstance(result, dict)
        assert "frontend_assets" in result or "backend_assets" in result
        
    def test_detect_missing_callable(self):
        """Test detect_missing can be called with basic parameters."""
        params = {
            "requirements": ["website", "mobile app"],
            "current_assets": ["logo", "content"],
            "scope_level": "standard"
        }
        
        result = detect_missing.run(params)
        
        # Should return expected structure
        assert isinstance(result, dict)
        
    def test_generate_lovable_spec_callable(self):
        """Test generate_lovable_spec can be called."""
        params = {
            "requirements": {"website": {"type": "website", "confidence": 0.8}},
            "business_context": {"business_type": "consulting", "client_tier": "business"}
        }
        
        result = generate_lovable_spec.run(params)
        
        # Should return expected structure  
        assert isinstance(result, dict)
        
    def test_generate_tasks_callable(self):
        """Test generate_tasks can be called."""
        params = {
            "requirements": [{"type": "website", "confidence": 0.8}],
            "project_scope": {"timeline": "2 months", "complexity": "medium"}
        }
        
        result = generate_tasks.run(params)
        
        # Should return expected structure
        assert isinstance(result, dict)
        
    def test_generate_timeline_callable(self):
        """Test generate_timeline can be called."""  
        params = {
            "tasks": {"task_breakdown": [{"name": "Setup", "duration": "1 week"}]},
            "project_constraints": {"deadline": "2 months", "resources": "small team"}
        }
        
        result = generate_timeline.run(params)
        
        # Should return expected structure
        assert isinstance(result, dict)
        
    def test_generate_summary_callable(self):
        """Test generate_summary can be called."""
        params = {
            "project_data": {
                "requirements": [{"type": "website"}],
                "timeline": "2 months", 
                "complexity": "medium"
            }
        }
        
        result = generate_summary.run(params)
        
        # Should return expected structure
        assert isinstance(result, dict)

    def test_cleaning_module_available(self):
        """Test cleaning module has expected functions."""
        assert hasattr(cleaning, 'clean_text')
        assert hasattr(cleaning, 'clean_whitespace') 
        assert hasattr(cleaning, 'normalize_email')
        
        # Test basic cleaning works
        cleaned = cleaning.clean_whitespace("  Test   Text  ")
        assert "Test Text" in cleaned

    def test_text_rules_module_available(self):
        """Test text_rules module has expected functions."""
        assert hasattr(text_rules, 'apply_text_rules')
        assert hasattr(text_rules, 'extract_patterns')
        assert hasattr(text_rules, 'classify_content')
        
        # Test basic rule application
        patterns = text_rules.extract_patterns("website development project")
        assert isinstance(patterns, dict)

    def test_all_tools_have_metadata(self):
        """Test all tools have get_tool_metadata function."""
        tools = [
            extract_assets, detect_missing, generate_lovable_spec, 
            generate_tasks, generate_timeline, generate_summary
        ]
        
        for tool in tools:
            assert hasattr(tool, 'get_tool_metadata')
            metadata = tool.get_tool_metadata()
            assert isinstance(metadata, dict)
            assert 'name' in metadata
            assert 'description' in metadata

    def test_skills_cross_tool_integration(self):
        """Test that skills modules work across tools."""
        # Test that validators work in different contexts
        assert validators.validate_confidence_score(0.75)
        assert not validators.validate_confidence_score(1.5)
        
        # Test that cleaning works with various inputs
        messy_text = "   Multiple   Spaces    And  \n  Newlines   "
        clean_text = cleaning.clean_whitespace(messy_text)
        assert "Multiple Spaces And" in clean_text
        
        # Test text rules work with business content
        business_text = "We need a website with e-commerce capabilities"
        classification = text_rules.classify_content(business_text)
        assert isinstance(classification, dict)
