"""
Unit tests for expand_requirements MCP tool.

Tests the deterministic requirement expansion functionality using
business logic templates and complexity assessment.
"""

import pytest
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from mcp_servers.intake import expand_requirements


class TestExpandRequirements:
    """Test cases for expand_requirements tool."""

    def test_website_requirement_expansion(self):
        """Test expanding website requirements."""
        parameters = {
            "requirements": [
                {"type": "website", "confidence": 0.8, "evidence": ["website"], "source": "structured"}
            ],
            "business_type": "consulting",
            "client_tier": "business",
        }
        
        result = expand_requirements.run(parameters)
        
        assert "expanded_requirements" in result
        assert "technical_implications" in result
        assert "estimated_complexity" in result
        assert "processing_metadata" in result
        
        # Should have expanded requirements
        assert len(result["expanded_requirements"]) > 0
        
        # Complexity should be valid
        assert result["estimated_complexity"] in ["low", "medium", "high"]
        
        # Should have technical implications
        assert isinstance(result["technical_implications"], list)

    def test_ecommerce_requirement_expansion(self):
        """Test expanding e-commerce requirements."""
        parameters = {
            "requirements": [
                {"type": "ecommerce", "confidence": 0.9, "evidence": ["store", "payment"], "source": "structured"}
            ],
            "business_type": "retail",
            "client_tier": "premium",
        }
        
        result = expand_requirements.run(parameters)
        
        assert "expanded_requirements" in result
        assert len(result["expanded_requirements"]) > 0
        
        # E-commerce should result in higher complexity
        assert result["estimated_complexity"] in ["medium", "high"]
        
        # Should have payment-related implications
        implications = result["technical_implications"]
        payment_related = any("payment" in impl.lower() or "pci" in impl.lower() for impl in implications)
        assert payment_related

    def test_mobile_app_requirement_expansion(self):
        """Test expanding mobile app requirements."""
        parameters = {
            "requirements": [
                {"type": "mobile_app", "confidence": 0.7, "evidence": ["mobile", "app"], "source": "conversational"}
            ],
            "business_type": "fintech",
            "client_tier": "business",
        }
        
        result = expand_requirements.run(parameters)
        
        assert "expanded_requirements" in result
        assert len(result["expanded_requirements"]) > 0
        
        # Mobile apps should have platform considerations
        expanded = result["expanded_requirements"]
        has_platform_info = any("platform" in req.get("description", "").lower() for req in expanded)
        assert has_platform_info

    def test_multiple_requirements_expansion(self):
        """Test expanding multiple requirements together."""
        parameters = {
            "requirements": [
                {"type": "website", "confidence": 0.8, "evidence": ["website"], "source": "structured"},
                {"type": "cms", "confidence": 0.6, "evidence": ["cms"], "source": "structured"},
                {"type": "integration", "confidence": 0.7, "evidence": ["integration"], "source": "structured"}
            ],
            "business_type": "media",
            "client_tier": "premium",
        }
        
        result = expand_requirements.run(parameters)
        
        assert "expanded_requirements" in result
        # Multiple requirements should result in more expanded requirements
        assert len(result["expanded_requirements"]) >= len(parameters["requirements"])
        
        # Complex multi-requirement projects should have higher complexity
        assert result["estimated_complexity"] in ["medium", "high"]

    def test_empty_requirements(self):
        """Test handling empty requirements list."""
        parameters = {
            "requirements": [],
            "business_type": "general",
            "client_tier": "starter",
        }
        
        result = expand_requirements.run(parameters)
        
        assert "expanded_requirements" in result
        assert "technical_implications" in result
        assert "estimated_complexity" in result
        
        # Should handle empty gracefully
        assert isinstance(result["expanded_requirements"], list)
        assert result["estimated_complexity"] == "low"

    def test_different_client_tiers(self):
        """Test that client tier affects requirement expansion."""
        base_requirements = [
            {"type": "website", "confidence": 0.8, "evidence": ["website"], "source": "structured"}
        ]
        
        # Test starter tier
        starter_params = {
            "requirements": base_requirements,
            "business_type": "consulting",
            "client_tier": "starter",
        }
        starter_result = expand_requirements.run(starter_params)
        
        # Test premium tier
        premium_params = {
            "requirements": base_requirements,
            "business_type": "consulting", 
            "client_tier": "premium",
        }
        premium_result = expand_requirements.run(premium_params)
        
        # Premium should have more comprehensive requirements
        assert len(premium_result["expanded_requirements"]) >= len(starter_result["expanded_requirements"])

    def test_healthcare_business_type(self):
        """Test healthcare-specific requirement expansion."""
        parameters = {
            "requirements": [
                {"type": "website", "confidence": 0.8, "evidence": ["website"], "source": "structured"}
            ],
            "business_type": "healthcare",
            "client_tier": "business",
        }
        
        result = expand_requirements.run(parameters)
        
        # Healthcare should include HIPAA considerations
        implications = result["technical_implications"]
        has_hipaa = any("hipaa" in impl.lower() or "compliance" in impl.lower() for impl in implications)
        assert has_hipaa

    def test_processing_metadata(self):
        """Test that processing metadata is correctly included."""
        parameters = {
            "requirements": [
                {"type": "website", "confidence": 0.8, "evidence": ["website"], "source": "structured"}
            ],
            "business_type": "consulting",
            "client_tier": "business",
        }
        
        result = expand_requirements.run(parameters)
        
        metadata = result["processing_metadata"]
        assert metadata["tool"] == "expand_requirements"
        assert metadata["version"] == "1.0.0"
        assert metadata["business_type"] == "consulting"
        assert metadata["client_tier"] == "business"
        assert metadata["original_count"] == 1

    def test_invalid_parameters(self):
        """Test handling of invalid parameters."""
        with pytest.raises(ValueError):
            expand_requirements.run({})  # Missing requirements
        
        with pytest.raises(ValueError):
            expand_requirements.run({"requirements": "not a list"})  # Invalid type
