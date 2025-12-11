"""
Tests for intake parsing functionality.

This module validates the behavior of intake processing tools
using synthetic fixture data with comprehensive assertions.
"""

import pytest
from typing import Any, Dict
from src.core.enums import ClientTier
from src.core.schema_definitions import IntakeSchema, ClientInfo
from tests.fixtures import load_intake_sample, get_available_samples, create_mock_intake_data


class TestIntakeParsing:
    """Test cases for intake parsing functionality with detailed validation."""
    
    def test_load_dm_noise_sample(self) -> None:
        """
        Test loading the direct message noise sample.
        
        Expected validation:
        - Content loaded successfully with expected client details
        - Noise patterns present but business content identifiable  
        - Key business information extractable despite casual conversation
        """
        content = load_intake_sample("dm_noise.txt")
        
        # Basic content validation
        assert content is not None, "DM noise sample should load successfully"
        assert len(content) > 100, "DM content should be substantial (>100 chars)"
        
        # Client information validation
        assert "TechCorp Solutions" in content, "Should contain client company name"
        assert "sarah.chen@techcorp.com" in content, "Should contain client email"
        
        # Noise pattern validation
        lines = content.split('\n')
        assert len(lines) >= 5, "DM should have multiple conversational turns"
        
        # Business content extraction validation
        business_keywords = ["CRM", "system", "integration", "budget", "timeline"]
        found_keywords = [kw for kw in business_keywords if kw.lower() in content.lower()]
        assert len(found_keywords) >= 2, f"Should find business keywords despite noise: {found_keywords}"
        
        # Casual conversation indicators (confirming noise is present)
        casual_indicators = ["hey", "yeah", "lol", "btw", "ok cool"]
        found_casual = [ci for ci in casual_indicators if ci.lower() in content.lower()]
        assert len(found_casual) >= 1, "Should contain casual conversation noise"
        
    def test_load_form_submission_sample(self) -> None:
        """
        Test loading the form submission sample.
        
        Expected validation:
        - Structured form data with clear field separation
        - Complete client information including business details
        - Detailed project requirements and scope definition
        - Budget and timeline information clearly specified
        """
        content = load_intake_sample("form_submission.txt")
        
        # Basic content validation
        assert content is not None, "Form submission should load successfully"
        assert len(content) > 200, "Form should contain substantial structured data"
        
        # Client information validation
        assert "GlobalTech Industries" in content, "Should contain company name"
        assert "E-commerce Platform Modernization" in content, "Should contain project title"
        
        # Form structure validation
        form_fields = ["name", "email", "company", "project", "budget", "timeline"]
        found_fields = [field for field in form_fields if field.lower() in content.lower()]
        assert len(found_fields) >= 4, f"Should have structured form fields: {found_fields}"
        
        # Requirements detail validation
        requirement_indicators = ["requirements", "features", "functionality", "needs"]
        found_requirements = [ri for ri in requirement_indicators if ri.lower() in content.lower()]
        assert len(found_requirements) >= 1, "Should contain detailed requirements"
        
        # Business context validation  
        business_terms = ["modernization", "platform", "scalable", "integration"]
        found_business = [bt for bt in business_terms if bt.lower() in content.lower()]
        assert len(found_business) >= 2, f"Should have business context: {found_business}"
        
    def test_load_email_thread_sample(self) -> None:
        """Test loading the email thread sample.""" 
        content = load_intake_sample("email_thread.txt")
        
        assert content is not None
        assert len(content) > 0
        assert "HealthPlus Medical Group" in content
        assert "HIPAA compliance" in content
        
    def test_get_available_samples(self) -> None:
        """Test getting list of available sample files."""
        samples = get_available_samples()
        
        assert isinstance(samples, list)
        assert len(samples) > 0
        assert "dm_noise.txt" in samples
        assert "form_submission.txt" in samples
        assert "email_thread.txt" in samples
        
    def test_intake_schema_validation(self) -> None:
        """Test intake schema validation with mock data."""
        mock_data = create_mock_intake_data()
        
        # Should be able to create IntakeSchema from mock data
        intake = IntakeSchema(**mock_data)
        
        assert intake.source_type == "email"
        assert intake.raw_content == "Mock intake content for testing"
        assert isinstance(intake.attachments, list)
        assert len(intake.attachments) == 0
        
    def test_intake_parsing_workflow_placeholder(self) -> None:
        """
        Placeholder test for intake parsing workflow.
        
        This test validates that synthetic inputs can be used to test
        the orchestrator validation process once the parsing tools
        are implemented.
        """
        # Load sample data
        dm_content = load_intake_sample("dm_noise.txt")
        form_content = load_intake_sample("form_submission.txt")
        email_content = load_intake_sample("email_thread.txt")
        
        # Create intake schemas
        dm_intake = IntakeSchema(
            source_type="direct_message",
            raw_content=dm_content,
        )
        
        form_intake = IntakeSchema(
            source_type="form_submission", 
            raw_content=form_content,
        )
        
        email_intake = IntakeSchema(
            source_type="email_thread",
            raw_content=email_content,
        )
        
        # Validate that all intakes were created successfully
        assert dm_intake.raw_content == dm_content
        assert form_intake.raw_content == form_content
        assert email_intake.raw_content == email_content
        
        # Future implementation will add:
        # - Parse requirements from each intake
        # - Identify missing information
        # - Validate completeness scores
        # - Test orchestrator workflow execution
        
    def test_client_tier_detection_placeholder(self) -> None:
        """
        Placeholder test for client tier detection from intake data.
        
        Future implementation will analyze intake content to suggest
        appropriate client tiers based on project complexity, budget,
        and requirements.
        """
        # Load different types of intake content
        simple_project = load_intake_sample("dm_noise.txt")  # Small CRM project
        complex_project = load_intake_sample("form_submission.txt")  # Large e-commerce
        healthcare_project = load_intake_sample("email_thread.txt")  # HIPAA-compliant
        
        # Future implementation will analyze content and suggest tiers:
        # - simple_project -> ClientTier.STARTER (small budget, basic features)
        # - complex_project -> ClientTier.PREMIUM (large budget, complex requirements)  
        # - healthcare_project -> ClientTier.BUSINESS (specialized compliance needs)
        
        # For now, validate that we can process all types
        assert len(simple_project) > 0
        assert len(complex_project) > 0
        assert len(healthcare_project) > 0
