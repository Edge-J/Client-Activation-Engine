#!/usr/bin/env python3
"""
Test script for deterministic intake parsing tools.

This tests the parse_intake, expand_requirements, and normalize_industry tools
to ensure they work correctly without LLM dependencies.
"""

import sys
import os
import json
import pytest

# Add the project root to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from mcp_servers.intake import parse_intake, expand_requirements, normalize_industry


@pytest.fixture
def sample_intake_result():
    """Fixture providing sample intake parsing result."""
    form_data = """
    Name: John Smith
    Email: john.smith@techcorp.com
    Company: TechCorp Solutions
    Phone: (555) 123-4567
    Project: Need a new company website with e-commerce capabilities
    Message: We're a technology consulting firm looking to build an online presence.
    We need a professional website with the ability to sell our software products online.
    Timeline: Need this completed in 2 months
    Budget: Around $15,000
    """
    
    parameters = {
        "input_data": form_data,
        "source_type": "auto_detect"
    }
    
    return parse_intake.run(parameters)


def test_form_parsing():
    """Test parsing a form submission."""
    print("Testing form submission parsing...")
    
    form_data = """
    Name: John Smith
    Email: john.smith@techcorp.com
    Company: TechCorp Solutions
    Phone: (555) 123-4567
    Project: Need a new company website with e-commerce capabilities
    Message: We're a technology consulting firm looking to build an online presence.
    We need a professional website with the ability to sell our software products online.
    Timeline: Need this completed in 2 months
    Budget: Around $15,000
    """
    
    parameters = {
        "input_data": form_data,
        "source_type": "auto_detect"
    }
    
    result = parse_intake.run(parameters)
    
    # Use assertions based on actual return structure
    assert "intake_data" in result
    assert "confidence_score" in result
    assert "data_quality" in result
    assert "processing_metadata" in result
    assert "John Smith" in result["intake_data"].get("client_name", "")
    assert result["intake_data"].get("contact_email") == "john.smith@techcorp.com"
    assert result["intake_data"].get("business_type") is not None
    assert result["confidence_score"] > 0


def test_requirement_expansion(sample_intake_result):
    """Test expanding requirements from parsed intake."""
    
    requirements = sample_intake_result["intake_data"].get("requirements", [])
    business_type = sample_intake_result["intake_data"].get("business_type", "general")
    
    parameters = {
        "requirements": requirements,
        "business_type": business_type,
        "client_tier": "business",
    }
    
    result = expand_requirements.run(parameters)
    
    # Use assertions based on actual return structure
    assert "expanded_requirements" in result
    assert "technical_implications" in result
    assert "estimated_complexity" in result
    assert "processing_metadata" in result
    assert len(result["expanded_requirements"]) >= len(requirements)
    assert result["estimated_complexity"] in ["low", "medium", "high"]
    assert isinstance(result["technical_implications"], list)


def test_industry_normalization():
    """Test industry normalization."""
    
    test_description = "Software development consultancy"
    
    parameters = {
        "business_description": test_description,
        "confidence_threshold": 0.5,
    }
    
    result = normalize_industry.run(parameters)
    
    # Use assertions based on actual return structure
    assert "normalized_industry" in result
    assert "confidence_score" in result
    assert "classification_evidence" in result
    assert "processing_metadata" in result
    assert result["confidence_score"] >= 0.0
    assert result["normalized_industry"] is not None
    assert isinstance(result["classification_evidence"], dict)


if __name__ == "__main__":
    import sys
    sys.exit(pytest.main([__file__]))
