"""
Unit tests for extract_assets MCP tool.

Tests the deterministic asset detection functionality using
file type patterns and location keywords.
"""

import os
import pytest
import sys

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "..", ".."))

from mcp_servers.analysis import extract_assets


class TestExtractAssets:
    """Test cases for extract_assets tool."""

    def test_logo_detection(self):
        """Test logo asset detection."""
        parameters = {
            "input_data": "We have our company logo in PNG format and a brand guide document.",
        }
        
        result = extract_assets.run(parameters)
        
        assert "detected_assets" in result
        assert "asset_summary" in result
        assert "processing_metadata" in result
        
        assets = result["detected_assets"]
        logo_assets = [asset for asset in assets if asset["type"] == "logo"]
        assert len(logo_assets) > 0
        
        # Should detect PNG format
        png_assets = [asset for asset in assets if "png" in asset["name"].lower()]
        assert len(png_assets) > 0

    def test_document_detection(self):
        """Test document asset detection."""
        parameters = {
            "input_data": "Please use our existing PDFs, Word documents, and Excel spreadsheets.",
        }
        
        result = extract_assets.run(parameters)
        
        assets = result["detected_assets"]
        doc_assets = [asset for asset in assets if asset["type"] == "document"]
        assert len(doc_assets) > 0
        
        # Should detect multiple document types
        doc_types = [asset["format"] for asset in doc_assets]
        assert "pdf" in doc_types or "word" in doc_types

    def test_image_detection(self):
        """Test image asset detection."""
        parameters = {
            "input_data": "We need to use photos from our gallery, JPEGs of products, and image files.",
        }
        
        result = extract_assets.run(parameters)
        
        assets = result["detected_assets"]
        image_assets = [asset for asset in assets if asset["type"] == "image"]
        assert len(image_assets) > 0
        
        # Should have confidence scores
        for asset in image_assets:
            assert "confidence" in asset
            assert 0.0 <= asset["confidence"] <= 1.0

    def test_video_detection(self):
        """Test video asset detection."""
        parameters = {
            "input_data": "Include our promotional videos, MP4 files, and video testimonials.",
        }
        
        result = extract_assets.run(parameters)
        
        assets = result["detected_assets"]
        video_assets = [asset for asset in assets if asset["type"] == "video"]
        assert len(video_assets) > 0

    def test_location_based_detection(self):
        """Test location-based asset detection."""
        parameters = {
            "input_data": "Files are stored in Google Drive folder and Dropbox shared directory.",
        }
        
        result = extract_assets.run(parameters)
        
        assets = result["detected_assets"]
        # Should detect cloud storage locations
        locations = [asset.get("location", "") for asset in assets]
        cloud_assets = any("google drive" in loc.lower() or "dropbox" in loc.lower() for loc in locations)
        assert cloud_assets

    def test_mixed_asset_types(self):
        """Test detection of multiple asset types."""
        parameters = {
            "input_data": """
            We have logos in our brand folder, product photos in JPEG format,
            PDF brochures, video demos in MP4, and audio files for the background music.
            All files are stored in our shared Google Drive.
            """,
        }
        
        result = extract_assets.run(parameters)
        
        assets = result["detected_assets"]
        asset_types = [asset["type"] for asset in assets]
        
        # Should detect multiple types
        assert "logo" in asset_types
        assert "image" in asset_types
        assert "document" in asset_types
        assert "video" in asset_types

    def test_asset_summary(self):
        """Test asset summary generation."""
        parameters = {
            "input_data": "We have 5 logos, 20 product images, and 3 PDF documents.",
        }
        
        result = extract_assets.run(parameters)
        
        summary = result["asset_summary"]
        assert "total_assets" in summary
        assert "by_type" in summary
        assert "by_format" in summary
        
        # Should have reasonable total
        assert summary["total_assets"] > 0

    def test_confidence_scoring(self):
        """Test confidence scoring for asset detection."""
        parameters = {
            "input_data": "Definitely have company logo and maybe some old photos somewhere.",
        }
        
        result = extract_assets.run(parameters)
        
        assets = result["detected_assets"]
        
        # Logo should have higher confidence than vague photo reference
        logo_assets = [asset for asset in assets if "logo" in asset["name"].lower()]
        photo_assets = [asset for asset in assets if "photo" in asset["name"].lower()]
        
        if logo_assets and photo_assets:
            assert logo_assets[0]["confidence"] >= photo_assets[0]["confidence"]

    def test_no_assets_detected(self):
        """Test handling when no assets are detected."""
        parameters = {
            "input_data": "We need to build everything from scratch with no existing materials.",
        }
        
        result = extract_assets.run(parameters)
        
        assert "detected_assets" in result
        assert "asset_summary" in result
        
        # Should handle gracefully with empty results
        assets = result["detected_assets"]
        summary = result["asset_summary"]
        assert isinstance(assets, list)
        assert summary["total_assets"] == 0

    def test_file_format_detection(self):
        """Test specific file format detection."""
        parameters = {
            "input_data": """
            Logo files: logo.svg, logo.png, logo.ai
            Documents: manual.pdf, specs.docx, data.xlsx
            Images: hero.jpg, gallery.jpeg, icons.webp
            """,
        }
        
        result = extract_assets.run(parameters)
        
        assets = result["detected_assets"]
        formats = [asset.get("format", "") for asset in assets]
        
        # Should detect various formats
        expected_formats = ["svg", "png", "pdf", "jpg", "jpeg"]
        detected_formats = [fmt for fmt in expected_formats if any(fmt in f for f in formats)]
        assert len(detected_formats) > 0

    def test_processing_metadata(self):
        """Test processing metadata is included."""
        parameters = {
            "input_data": "Company logos and brand assets",
        }
        
        result = extract_assets.run(parameters)
        
        metadata = result["processing_metadata"]
        assert metadata["tool"] == "extract_assets"
        assert metadata["version"] == "1.0.0"
        assert "input_length" in metadata
        assert "assets_found" in metadata

    def test_asset_categorization(self):
        """Test that assets are properly categorized."""
        parameters = {
            "input_data": "Brand guidelines PDF, company logo SVG, product catalog images",
        }
        
        result = extract_assets.run(parameters)
        
        assets = result["detected_assets"]
        
        # Should have proper categories
        for asset in assets:
            assert "type" in asset
            assert asset["type"] in ["logo", "image", "document", "video", "audio", "other"]
            assert "name" in asset
            assert "confidence" in asset

    def test_missing_assets_detection(self):
        """Test detection of missing asset references."""
        parameters = {
            "input_data": "Will need logo design and professional photos to be created",
        }
        
        result = extract_assets.run(parameters)
        
        # Should detect missing assets that need to be created
        summary = result["asset_summary"]
        if "missing_assets" in summary:
            assert isinstance(summary["missing_assets"], list)

    def test_empty_input(self):
        """Test handling of empty input."""
        parameters = {
            "input_data": "",
        }
        
        result = extract_assets.run(parameters)
        
        assert "detected_assets" in result
        assert "asset_summary" in result
        assert result["asset_summary"]["total_assets"] == 0

    def test_invalid_parameters(self):
        """Test handling of invalid parameters."""
        with pytest.raises(ValueError, match="Missing required parameter"):
            extract_assets.run({})  # Missing input_data
