#!/usr/bin/env python3
"""
Client Activation Engine - Main Entry Point

This script serves as the primary entry point for the Client Activation Engine.
It orchestrates the entire client onboarding process from intake to asset generation.

Usage:
    python run.py --mode intake --input data/input/client_submission.txt
    python run.py --mode analysis --client-id 12345
    python run.py --mode generate --requirements data/output/requirements_12345.json
    python run.py --mode orchestrator --config config/orchestrator_config.yaml

Environment Configuration:
    Ensure .env file is configured with necessary API keys and settings.
    See README.md for detailed setup instructions.
"""

import argparse
import asyncio
import logging
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import core modules (to be implemented)
# from src.orchestrator.loop import OrchestrationLoop
# from src.sandbox.sandbox_runner import SandboxRunner
# from src.core.schema_definitions import IntakeSchema


def setup_logging() -> None:
    """
    Configure logging based on config/logging_config.yaml with safety guards.
    
    Config loading order:
    1. config/logging_config.yaml (primary configuration)
    2. Basic fallback if config file missing/invalid
    3. Environment variable LOG_LEVEL override if present
    """
    import yaml
    from logging.config import dictConfig
    
    config_path = Path("config/logging_config.yaml")
    
    try:
        if config_path.exists():
            with open(config_path, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f)
                
            # Validate config structure
            if not isinstance(config, dict):
                raise ValueError("Logging config must be a dictionary")
                
            if "version" not in config:
                raise ValueError("Logging config missing required 'version' field")
                
            dictConfig(config)
            
            # Get logger after dictConfig
            logger = logging.getLogger(__name__)
            logger.info(f"Loaded logging configuration from {config_path}")
            
        else:
            raise FileNotFoundError(f"Logging config not found: {config_path}")
            
    except (FileNotFoundError, ValueError, yaml.YAMLError, KeyError) as e:
        # Fallback to basic configuration with error logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("logs/client_activation.log"),
                logging.StreamHandler(sys.stdout),
            ],
        )
        
        logger = logging.getLogger(__name__)
        logger.warning(f"Failed to load logging config: {e}")
        logger.info("Using fallback logging configuration")
    
    # Allow environment variable override for log level
    import os
    env_log_level = os.getenv("LOG_LEVEL")
    if env_log_level:
        try:
            level = getattr(logging, env_log_level.upper())
            logging.getLogger().setLevel(level)
            logging.getLogger(__name__).info(f"Log level overridden to: {env_log_level}")
        except AttributeError:
            logging.getLogger(__name__).warning(f"Invalid LOG_LEVEL: {env_log_level}")


def validate_environment() -> bool:
    """
    Validate required environment variables and paths with safety guards.
    
    Environment validation order:
    1. Check for .env file and load if present
    2. Validate required directories (create if missing)
    3. Check essential environment variables
    4. Validate config files exist and are readable
    """
    import os
    
    logger = logging.getLogger(__name__)
    
    # Check for .env file
    env_file = Path(".env")
    if not env_file.exists():
        logger.warning("No .env file found - using system environment variables only")
        logger.info("Create a .env file for local development configuration")
    
    # Ensure required directories exist
    required_dirs = ["data/input", "data/output", "logs", "config"]
    missing_dirs = []
    
    for dir_path in required_dirs:
        dir_obj = Path(dir_path)
        try:
            dir_obj.mkdir(parents=True, exist_ok=True)
            if not dir_obj.is_dir():
                missing_dirs.append(dir_path)
        except (OSError, PermissionError) as e:
            logger.error(f"Failed to create directory {dir_path}: {e}")
            missing_dirs.append(dir_path)
    
    if missing_dirs:
        logger.error(f"Failed to create required directories: {missing_dirs}")
        return False
    
    # Check essential environment variables (with defaults)
    env_checks = {
        "OPENAI_API_KEY": "Required for LLM operations",
        "PYTHONPATH": "Should include project root for imports",
    }
    
    missing_env_vars = []
    for var_name, description in env_checks.items():
        if not os.getenv(var_name):
            missing_env_vars.append(f"{var_name} ({description})")
    
    if missing_env_vars:
        logger.warning("Missing environment variables:")
        for var_info in missing_env_vars:
            logger.warning(f"  - {var_info}")
        logger.info("Some features may not work without proper environment setup")
    
    # Validate essential config files exist
    required_configs = [
        "config/logging_config.yaml",
        "config/model_config.yaml", 
        "config/orchestrator_config.yaml",
        "config/system_constraints.yaml",
    ]
    
    missing_configs = []
    for config_path in required_configs:
        if not Path(config_path).exists():
            missing_configs.append(config_path)
    
    if missing_configs:
        logger.error("Missing required configuration files:")
        for config_file in missing_configs:
            logger.error(f"  - {config_file}")
        logger.error("Run setup scripts to generate default configurations")
        return False
    
    # Validate config files are readable
    for config_path in required_configs:
        try:
            with Path(config_path).open(encoding="utf-8") as f:
                content = f.read()
                if len(content.strip()) == 0:
                    logger.warning(f"Configuration file {config_path} is empty")
        except (OSError, PermissionError, UnicodeDecodeError) as e:
            logger.error(f"Cannot read configuration file {config_path}: {e}")
            return False
    
    logger.info("Environment validation completed successfully")
    return True


async def run_intake_mode(input_file: Path) -> None:
    """Process client intake from raw input files"""
    print(f"🔍 Processing intake from: {input_file}")
    # TODO: Implement intake processing
    pass


async def run_analysis_mode(client_id: str) -> None:
    """Run analysis on client requirements"""
    print(f"📊 Running analysis for client: {client_id}")
    # TODO: Implement analysis logic
    pass


async def run_generation_mode(requirements_file: Path) -> None:
    """Generate assets based on requirements"""
    print(f"🏗️ Generating assets from: {requirements_file}")
    # TODO: Implement asset generation
    pass


async def run_orchestrator_mode(config_file: Path) -> None:
    """Run the full orchestration loop"""
    print(f"🎯 Starting orchestrator with config: {config_file}")
    # TODO: Implement orchestration loop
    pass


def main() -> None:
    """Main entry point for the Client Activation Engine"""
    parser = argparse.ArgumentParser(
        description="Client Activation Engine - Automate client onboarding"
    )
    parser.add_argument(
        "--mode",
        choices=["intake", "analysis", "generate", "orchestrator"],
        required=True,
        help="Operation mode to run",
    )
    parser.add_argument("--input", type=Path, help="Input file path")
    parser.add_argument("--client-id", help="Client identifier")
    parser.add_argument("--requirements", type=Path, help="Requirements file path")
    parser.add_argument("--config", type=Path, help="Configuration file path")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")

    args = parser.parse_args()

    # Setup
    setup_logging()
    if not validate_environment():
        sys.exit(1)

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    # Route to appropriate mode
    try:
        if args.mode == "intake":
            if not args.input:
                parser.error("--input required for intake mode")
            asyncio.run(run_intake_mode(args.input))
        elif args.mode == "analysis":
            if not args.client_id:
                parser.error("--client-id required for analysis mode")
            asyncio.run(run_analysis_mode(args.client_id))
        elif args.mode == "generate":
            if not args.requirements:
                parser.error("--requirements required for generate mode")
            asyncio.run(run_generation_mode(args.requirements))
        elif args.mode == "orchestrator":
            config_file = args.config or Path("config/orchestrator_config.yaml")
            asyncio.run(run_orchestrator_mode(config_file))

        print("✅ Operation completed successfully")

    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Error: {e}")
        logging.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
