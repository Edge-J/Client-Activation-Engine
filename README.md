# Client Activation Engine

Automate onboarding, requirement extraction, missing-info detection, asset organization, and build-spec generation so OmniSeen can onboard 20+ clients simultaneously with zero manual bottlenecks.

## Overview

The Client Activation Engine is a comprehensive system designed to streamline the client onboarding process from initial intake to final asset generation. It uses a combination of automated parsing, requirement analysis, and orchestrated workflows to handle multiple clients efficiently and simultaneously.

## Features

- **Multi-source Intake Processing**: Handle emails, forms, direct messages, and file uploads
- **Intelligent Requirements Extraction**: Parse unstructured input to identify functional and technical requirements
- **Gap Analysis**: Automatically detect missing information and generate follow-up questions
- **Tiered Service Management**: Support for Starter, Business, and Premium client tiers
- **Safe Code Execution**: Sandbox environment for dynamic code generation and testing
- **Orchestrated Workflows**: Automated multi-step processes with error handling and recovery
- **Asset Generation**: Automated creation of documentation, code, and build specifications

## Project Structure

### Core Directories

```
├── run.py                      # Main entry point
├── config/                     # Configuration files
│   ├── logging_config.yaml     # Logging configuration
│   ├── orchestrator_config.yaml # Workflow orchestration settings
│   ├── system_constraints.yaml # System limits and client tier definitions
│   └── model_config.yaml       # LLM and AI model settings
├── src/                        # Source code
│   ├── core/                   # Shared schemas, enums, and validators
│   ├── handlers/               # Error handling and utilities
│   ├── llm/                    # Language model integration
│   ├── mcp_tools/              # Model Context Protocol tool implementations
│   ├── orchestrator/           # Workflow orchestration and execution
│   └── sandbox/                # Safe code execution environment
├── mcp_servers/                # Standalone tool modules
│   ├── intake/                 # Input processing tools
│   ├── analysis/               # Requirement analysis tools
│   ├── generation/             # Asset generation tools
│   └── skills/                 # Reusable utility tools
├── data/                       # Data directories
│   ├── input/                  # Raw client intake files
│   └── output/                 # Generated assets and results
├── logs/                       # Application logs and debugging output
├── tests/                      # Test suite
│   └── fixtures/               # Test data and synthetic inputs
└── notebooks/                  # Analysis and testing notebooks
```

### Key Components

#### Orchestrator System
- **Orchestration Loop** (`src/orchestrator/loop.py`): Main reasoning loop that coordinates workflow execution
- **Executor Interface** (`src/orchestrator/executor.py`): Safe code execution interface with sandbox integration
- **Tools Interface** (`src/orchestrator/tools_interface.py`): Discovery and execution of MCP tools
- **Memory Management** (`src/orchestrator/memory.py`): Context and conversation state management

#### Sandbox Environment
- **Sandbox Runner** (`src/sandbox/sandbox_runner.py`): Secure Python code execution with resource limits
- **Execution Constraints**: Memory limits, timeout controls, and import restrictions
- **Output Directory Isolation**: All file operations restricted to designated output paths

#### Core Schemas and Validation
- **Enums** (`src/core/enums.py`): Client tiers, asset types, processing states
- **Schema Definitions** (`src/core/schema_definitions.py`): Pydantic models for all data structures
- **Validators** (`src/core/validators.py`): Data validation and constraint checking

## Getting Started

### Installation

1. Clone the repository:
```bash
git clone https://github.com/Edge-J/Client-Activation-Engine.git
cd Client-Activation-Engine
```

2. Install dependencies:
```bash
pip install -e .
```

3. Install development dependencies:
```bash
pip install -e ".[dev]"
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and configuration
```

### Basic Usage

#### Run Complete Orchestration Workflow
```bash
python run.py --mode orchestrator --config config/orchestrator_config.yaml
```

#### Process Client Intake
```bash
python run.py --mode intake --input data/input/client_submission.txt
```

#### Run Requirements Analysis
```bash
python run.py --mode analysis --client-id 12345
```

#### Generate Assets
```bash
python run.py --mode generate --requirements data/output/requirements_12345.json
```

### Configuration

The system uses YAML configuration files in the `config/` directory:

- **System Constraints**: Client tier limits, asset type restrictions, processing limits
- **Orchestrator Config**: Loop parameters, tool settings, workflow templates
- **Logging Config**: Log levels, file rotation, output destinations

### Client Tiers

The system supports three client service tiers:

#### Starter Tier
- Max 5 assets per project
- Basic intake and analysis
- Template-based generation
- Single concurrent workflow

#### Business Tier  
- Max 20 assets per project
- Advanced analysis with custom generation
- Workflow automation
- Up to 3 concurrent workflows

#### Premium Tier
- Max 100 assets per project
- Enterprise-grade features
- Full automation and custom integrations
- Up to 10 concurrent workflows

## Synthetic Input Validation

The system includes comprehensive test fixtures for validating intake processing:

### Test Fixtures (`tests/fixtures/intake_samples/`)
- **Direct Message** (`dm_noise.txt`): Informal client communication
- **Form Submission** (`form_submission.txt`): Structured project requirements
- **Email Thread** (`email_thread.txt`): Professional multi-party conversation

These fixtures enable testing of:
- Intake parsing across different source types
- Requirements extraction and validation
- Missing information detection
- Client tier assessment
- Orchestrator workflow execution

## Development

### Running Tests
```bash
pytest tests/
```

### Code Quality
```bash
# Format code
black src/ tests/

# Lint code  
ruff check src/ tests/

# Type checking
mypy src/
```

### Adding New Tools

1. Create tool module in appropriate `mcp_servers/` subdirectory
2. Implement tool interface following MCP protocol
3. Add tool discovery metadata
4. Create tests in `tests/test_tools/`
5. Update documentation

## Security and Compliance

### Sandbox Security
- Resource limits (memory, CPU, disk)
- Import restrictions and validation
- File system isolation
- Execution timeouts

### Data Protection
- Input sanitization and validation
- Output sanitization for generated code
- Audit trails for all operations
- Configurable data retention policies

### Compliance Features
- HIPAA-compliant processing modes
- PCI DSS considerations for payment data
- GDPR compliance for EU data
- SOC 2 audit trail generation

## Monitoring and Logging

### Log Categories
- Application events and workflow progress
- Error tracking and debugging
- Performance metrics and timing
- Security events and access logs

### Health Monitoring
- Resource usage tracking
- Success/failure rate monitoring
- Performance degradation alerts
- Automated health checks

## Future Roadmap

### LLM Integration
- Natural language processing for intake parsing
- Intelligent requirement extraction
- Dynamic question generation
- Automated asset generation

### Enterprise Features  
- Multi-tenant support
- Advanced workflow customization
- External system integrations
- Real-time collaboration tools

### Scalability Enhancements
- Distributed processing
- Cloud-native deployment
- Auto-scaling capabilities
- Load balancing and failover

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Run the test suite: `pytest`
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

For questions, issues, or feature requests:
- Create an issue on GitHub
- Contact the development team at development@omniseen.com
- Review the documentation in `/docs` (coming soon)
