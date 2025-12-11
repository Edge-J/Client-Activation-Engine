"""
Unit tests for normalize_industry MCP tool.

Tests the deterministic industry classification functionality using
pattern matching and confidence scoring.
"""

import os
import pytest
import sys

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from mcp_servers.intake import normalize_industry


class TestNormalizeIndustry:
    """Test cases for normalize_industry tool."""

    def test_healthcare_classification(self):
        """Test healthcare industry classification."""
        parameters = {
            "business_description": "We are a medical practice providing HIPAA-compliant patient care",
            "confidence_threshold": 0.5,
        }
        
        result = normalize_industry.run(parameters)
        
        assert "normalized_industry" in result
        assert "confidence_score" in result
        assert "classification_evidence" in result
        assert "processing_metadata" in result
        
        assert result["normalized_industry"] == "healthcare"
        assert result["confidence_score"] > 0.5

    def test_ecommerce_classification(self):
        """Test e-commerce industry classification."""
        parameters = {
            "business_description": "Online retail store selling fashion products with payment processing",
            "confidence_threshold": 0.3,
        }
        
        result = normalize_industry.run(parameters)
        
        assert result["normalized_industry"] == "ecommerce"
        assert result["confidence_score"] > 0.3
        
        # Should have evidence
        evidence = result["classification_evidence"]
        assert isinstance(evidence, dict)
        assert "matched_primary_keywords" in evidence

    def test_fintech_classification(self):
        """Test fintech industry classification."""
        parameters = {
            "business_description": "Financial services platform for cryptocurrency trading and payments",
            "confidence_threshold": 0.4,
        }
        
        result = normalize_industry.run(parameters)
        
        assert result["normalized_industry"] == "fintech"
        assert result["confidence_score"] > 0.4

    def test_technology_classification(self):
        """Test technology/software classification."""
        parameters = {
            "business_description": "Software development consultancy building SaaS platforms",
            "confidence_threshold": 0.5,
        }
        
        result = normalize_industry.run(parameters)
        
        # Could be classified as either technology or saas
        assert result["normalized_industry"] in ["technology", "saas"]
        assert result["confidence_score"] > 0.5

    def test_education_classification(self):
        """Test education industry classification."""
        parameters = {
            "business_description": "University offering online courses and learning management systems",
            "confidence_threshold": 0.5,
        }
        
        result = normalize_industry.run(parameters)
        
        assert result["normalized_industry"] == "education"
        assert result["confidence_score"] > 0.5

    def test_general_fallback(self):
        """Test fallback to general classification."""
        parameters = {
            "business_description": "Random business with no clear industry indicators",
            "confidence_threshold": 0.8,
        }
        
        result = normalize_industry.run(parameters)
        
        assert "normalized_industry" in result
        # Should fall back to general or have low confidence
        assert result["confidence_score"] < 0.8 or result["normalized_industry"] == "general"

    def test_confidence_threshold_filtering(self):
        """Test confidence threshold filtering."""
        # High threshold should be more restrictive
        high_threshold_params = {
            "business_description": "We do some tech stuff occasionally",
            "confidence_threshold": 0.9,
        }
        
        result = normalize_industry.run(high_threshold_params)
        
        # With high threshold, should have low confidence or general classification
        assert result["confidence_score"] < 0.9 or result["normalized_industry"] == "general"

    def test_alternative_matches(self):
        """Test that alternative matches are provided."""
        parameters = {
            "business_description": "Healthcare technology platform for medical professionals",
            "confidence_threshold": 0.3,
        }
        
        result = normalize_industry.run(parameters)
        
        assert "alternative_matches" in result
        # Should have alternatives since this could be healthcare or technology
        alternatives = result["alternative_matches"]
        assert isinstance(alternatives, list)

    def test_classification_evidence(self):
        """Test that classification evidence is comprehensive."""
        parameters = {
            "business_description": "Online shopping platform with payment processing and inventory management",
            "confidence_threshold": 0.5,
        }
        
        result = normalize_industry.run(parameters)
        
        evidence = result["classification_evidence"]
        assert "matched_primary_keywords" in evidence
        assert "matched_secondary_keywords" in evidence
        assert "total_matches" in evidence
        
        # Should have matched e-commerce keywords
        primary_keywords = evidence["matched_primary_keywords"]
        assert len(primary_keywords) > 0

    def test_processing_metadata(self):
        """Test processing metadata is included."""
        parameters = {
            "business_description": "Software consulting firm",
            "confidence_threshold": 0.5,
        }
        
        result = normalize_industry.run(parameters)
        
        metadata = result["processing_metadata"]
        assert metadata["tool"] == "normalize_industry"
        assert metadata["version"] == "1.0.0"
        assert "text_length" in metadata
        assert "industries_evaluated" in metadata

    def test_empty_description(self):
        """Test handling of empty business description."""
        parameters = {
            "business_description": "",
            "confidence_threshold": 0.5,
        }
        
        result = normalize_industry.run(parameters)
        
        # Should handle empty description gracefully
        assert "error" in result
        assert result["confidence_score"] == 0.0

    def test_context_data_integration(self):
        """Test integration with context data."""
        parameters = {
            "business_description": "Professional services",
            "context_data": {
                "industry_hints": ["legal", "attorney"],
                "business_keywords": ["law", "litigation"],
            },
            "confidence_threshold": 0.5,
        }
        
        result = normalize_industry.run(parameters)
        
        # Should use context to improve classification
        assert "normalized_industry" in result
        assert result["confidence_score"] >= 0.0

    def test_multiple_industry_indicators(self):
        """Test handling of multiple strong industry indicators."""
        parameters = {
            "business_description": "Healthcare fintech startup providing medical payment solutions",
            "confidence_threshold": 0.4,
        }
        
        result = normalize_industry.run(parameters)
        
        # Should pick one primary industry
        assert result["normalized_industry"] in ["healthcare", "fintech"]
        
        # Should have alternatives
        alternatives = result["alternative_matches"]
        assert len(alternatives) > 0

    def test_invalid_parameters(self):
        """Test handling of invalid parameters."""
        # Missing business_description should be handled
        with pytest.raises(Exception):  # Could be KeyError or custom exception
            normalize_industry.run({"confidence_threshold": 0.5})

    def test_confidence_levels(self):
        """Test confidence level categorization."""
        parameters = {
            "business_description": "Medical clinic providing healthcare services to patients",
            "confidence_threshold": 0.3,
        }
        
        result = normalize_industry.run(parameters)
        
        assert "confidence_level" in result
        assert result["confidence_level"] in ["low", "medium", "high"]
        
        # Strong healthcare indicators should give high confidence
        assert result["confidence_level"] in ["medium", "high"]
