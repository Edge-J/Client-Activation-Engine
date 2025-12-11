"""
MCP Servers - Model Context Protocol Tool Modules

This directory contains standalone tool modules for the Client Activation Engine,
organized by functional area. Each subdirectory contains tools that can be
discovered and executed by the orchestration loop.

Directory Structure:
- intake/: Tools for processing raw client inputs and extracting structured data
- analysis/: Tools for analyzing requirements and identifying missing information
- generation/: Tools for generating assets, documentation, and build specifications
- skills/: Reusable skills and utilities that can be composed into workflows

Each tool module should implement the MCP protocol interface and be discoverable
via the tools_interface module in the orchestrator package.
"""
