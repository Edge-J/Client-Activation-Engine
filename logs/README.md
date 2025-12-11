# Client Activation Engine - Logs Directory

This directory contains log outputs from the sandbox/orchestrator for debugging and monitoring purposes.

## Log Files

### Application Logs
- `client_activation.log` - Main application events and general logging
- `errors.log` - Error tracking and debugging information
- `orchestrator.log` - Workflow execution details and orchestration events
- `sandbox_execution.log` - Code execution and validation logs
- `performance.log` - Performance metrics and timing information

## Log Configuration

Log configuration is managed through `config/logging_config.yaml`. The logging system uses:

- **Rotating file handlers** to manage log file sizes
- **JSON formatting** for structured logs where applicable
- **Multiple log levels** (DEBUG, INFO, WARNING, ERROR)
- **Separate loggers** for different components

## Log Retention

Logs are retained according to the following schedule:
- Processing logs: 30 days
- Error logs: 14 days
- Performance logs: 30 days (configurable)

## Monitoring Integration

Future monitoring integration will:
- Send structured logs to monitoring systems
- Set up alerts based on error rates and performance thresholds
- Provide dashboards for operational visibility

## Log Analysis

For log analysis and debugging:
1. Use `tail -f logs/client_activation.log` to monitor real-time activity
2. Search for specific client IDs or workflow steps using `grep`
3. Analyze performance metrics in `performance.log` for optimization opportunities
4. Review `orchestrator.log` for workflow execution patterns and issues

## Security Considerations

- Log files may contain sensitive information - ensure proper access controls
- Client data in logs should be sanitized or encrypted
- Regular log rotation prevents disk space issues
- Audit trails are maintained for compliance requirements
