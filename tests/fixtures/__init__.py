"""
Test fixtures for the Client Activation Engine.

This module provides helper functions to load test fixtures and mock data
for validating intake parsing and other system components.
"""

from pathlib import Path
from typing import Any

# Path to fixtures directory
FIXTURES_DIR = Path(__file__).parent


def load_intake_sample(filename: str) -> str:
    """
    Load a sample intake file for testing.
    
    Args:
        filename: Name of the sample file (e.g., "dm_noise.txt")
        
    Returns:
        Content of the sample file as string
    """
    sample_path = FIXTURES_DIR / "intake_samples" / filename
    if not sample_path.exists():
        msg = f"Sample file not found: {filename}"
        raise FileNotFoundError(msg)
    
    return sample_path.read_text(encoding="utf-8")


def get_available_samples() -> list[str]:
    """
    Get list of available intake sample files.
    
    Returns:
        List of sample filenames
    """
    samples_dir = FIXTURES_DIR / "intake_samples"
    if not samples_dir.exists():
        return []
    
    return [f.name for f in samples_dir.glob("*.txt")]


def create_mock_client_data() -> dict[str, Any]:
    """
    Create mock client data for testing.
    
    Returns:
        Dictionary with mock client information
    """
    return {
        "name": "Test Client Corp",
        "tier": "business",
        "contact_email": "test@testclient.com",
        "contact_name": "John Doe",
        "notes": "Mock client for testing purposes",
    }


def create_mock_intake_data(source_type: str = "email") -> dict[str, Any]:
    """
    Create mock intake data for testing.
    
    Args:
        source_type: Type of intake source
        
    Returns:
        Dictionary with mock intake data
    """
    return {
        "source_type": source_type,
        "raw_content": "Mock intake content for testing",
        "attachments": [],
        "metadata": {
            "timestamp": "2024-03-15T10:30:00Z",
            "source_ip": "192.168.1.100",
            "user_agent": "Test Client 1.0",
        },
    }
