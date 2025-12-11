# Logging Configuration Documentation

This document describes the comprehensive logging system for the Client Activation Engine, including configuration options, log levels, rotation policies, and troubleshooting guidance.

## Overview

The Client Activation Engine uses a sophisticated logging system built on Python's standard `logging` module with YAML-based configuration. The system provides structured logging, automatic log rotation, and multiple output destinations for different log levels.

## Configuration Architecture

### Configuration Loading Order

The logging system follows a hierarchical configuration approach:

1. **Primary**: `config/logging_config.yaml` (main configuration file)
2. **Fallback**: Basic console/file logging if primary config fails
3. **Override**: `LOG_LEVEL` environment variable can override configured levels
4. **Safety**: Automatic creation of log directory and fallback handling

### Configuration File Structure

```yaml
# config/logging_config.yaml
version: 1
disable_existing_loggers: false

formatters:
  default:
    format: "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
  detailed:
    format: "%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(funcName)s:%(lineno)d - %(message)s"
  json:
    format: "%(asctime)s %(levelname)s %(name)s %(message)s"
    class: pythonjsonlogger.jsonlogger.JsonFormatter

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: default
    stream: ext://sys.stdout

  file_handler:
    class: logging.handlers.RotatingFileHandler
    level: DEBUG
    formatter: detailed
    filename: logs/client_activation.log
    maxBytes: 10485760  # 10MB
    backupCount: 5
    encoding: utf8

  error_file:
    class: logging.handlers.RotatingFileHandler
    level: ERROR
    formatter: detailed
    filename: logs/errors.log
    maxBytes: 10485760  # 10MB
    backupCount: 10
    encoding: utf8

loggers:
  src.orchestrator:
    level: DEBUG
    handlers: [console, file_handler]
    propagate: false
    
  src.llm:
    level: DEBUG
    handlers: [console, file_handler]
    propagate: false
    
  src.sandbox:
    level: INFO
    handlers: [console, file_handler, error_file]
    propagate: false

root:
  level: INFO
  handlers: [console, file_handler, error_file]
```

## Log Levels and Usage Guidelines

### Level Hierarchy

| Level | Priority | Use Case | Example |
|-------|----------|----------|---------|
| `CRITICAL` | 50 | System failures that prevent operation | "Database connection failed - system cannot start" |
| `ERROR` | 40 | Errors that affect functionality but don't stop operation | "Failed to parse client intake - skipping file" |
| `WARNING` | 30 | Important issues that need attention but don't break functionality | "API rate limit approaching - throttling requests" |
| `INFO` | 20 | General information about system operation | "Processing client intake for GlobalTech Industries" |
| `DEBUG` | 10 | Detailed diagnostic information | "LLM request payload: {...}" |

### Module-Specific Logging Patterns

#### Orchestrator Module (`src.orchestrator`)
```python
import logging

logger = logging.getLogger(__name__)

# Workflow lifecycle events
logger.info("Starting orchestration loop for client %s", client_id)
logger.debug("Workflow state: %s", workflow.current_state)
logger.error("Workflow execution failed: %s", error_details)

# Decision tracking
logger.info("Decision point: %s - Selected action: %s", decision_point, action)
```

#### LLM Module (`src.llm`) 
```python
import logging

logger = logging.getLogger(__name__)

# API interactions
logger.debug("LLM request - Model: %s, Tokens: %d", model_name, token_count)
logger.info("LLM response received - Duration: %.2fs", response_time)
logger.warning("Token limit approaching: %d/%d used", used_tokens, limit)
logger.error("LLM API error: %s", api_error)
```

#### Sandbox Module (`src.sandbox`)
```python
import logging

logger = logging.getLogger(__name__)

# Execution tracking
logger.info("Executing code in sandbox - Timeout: %ds", timeout)
logger.debug("Sandbox environment: %s", environment_details)
logger.warning("Code execution exceeded memory limit: %dMB", memory_usage)
logger.error("Sandbox security violation: %s", violation_details)
```

## Log File Organization

### Directory Structure

```
logs/
├── client_activation.log          # Main application log (rotated)
├── client_activation.log.1        # Previous rotation (compressed)
├── client_activation.log.2        # Older rotation
├── errors.log                     # Error-level events only
├── errors.log.1                   # Previous error log rotation  
├── orchestrator/                  # Module-specific logs (optional)
│   ├── workflow_decisions.log
│   └── memory_operations.log
└── audit/                         # Compliance and audit logs
    ├── client_data_access.log
    └── code_generation.log
```

### Log Rotation Policies

#### Standard Application Logs
- **Size limit**: 10MB per file
- **Backup count**: 5 files retained
- **Compression**: Automatic after rotation
- **Retention**: ~50MB total per log stream

#### Error Logs  
- **Size limit**: 10MB per file
- **Backup count**: 10 files retained  
- **Compression**: Automatic after rotation
- **Retention**: ~100MB total (longer retention for debugging)

#### Audit Logs
- **Size limit**: 100MB per file
- **Backup count**: 50 files retained
- **Compression**: Automatic after rotation  
- **Retention**: ~5GB total (compliance requirements)

## Performance Considerations

### Logging Performance Guidelines

1. **Use lazy evaluation for expensive operations**:
   ```python
   # Good - only evaluates if DEBUG level active
   logger.debug("Complex data: %s", lambda: json.dumps(complex_data, indent=2))
   
   # Avoid - always evaluates even if not logged
   logger.debug(f"Complex data: {json.dumps(complex_data, indent=2)}")
   ```

2. **Batch related log entries**:
   ```python
   # Efficient for multiple related entries
   with logger_context(client_id=client_id):
       logger.info("Starting analysis")
       logger.debug("Analysis parameters: %s", params)
       logger.info("Analysis completed")
   ```

3. **Use appropriate log levels**:
   - DEBUG: Only enable in development or detailed troubleshooting
   - INFO: Safe for production with normal verbosity
   - WARNING/ERROR: Always captured regardless of level settings

### Memory and Disk Management

- **Buffer size**: 8KB default for file handlers (configurable)
- **Async logging**: Available for high-throughput scenarios
- **Log compression**: Automatic to reduce disk usage
- **Cleanup automation**: Old logs automatically removed based on retention policy

## Environment-Specific Configuration

### Development Environment

```yaml
# Optimized for debugging and development
root:
  level: DEBUG
  handlers: [console, file_handler]

loggers:
  src:
    level: DEBUG
    propagate: false
```

### Production Environment

```yaml
# Optimized for performance and monitoring
root:
  level: INFO  
  handlers: [file_handler, error_file, monitoring_handler]

loggers:
  src.orchestrator:
    level: INFO
    handlers: [file_handler, audit_handler]
    
  src.sandbox:
    level: WARNING  # Higher threshold for production
```

### Testing Environment

```yaml
# Minimal logging to avoid test output pollution
root:
  level: WARNING
  handlers: [memory_handler]  # In-memory only during tests
```

## Monitoring and Alerting Integration

### Structured Logging for Monitoring

```python
# Use structured logging for monitoring systems
logger.info(
    "Client workflow completed",
    extra={
        "client_id": client_id,
        "workflow_duration_ms": duration,
        "assets_generated": asset_count,
        "success": True,
        "tier": client_tier.value
    }
)
```

### Alert-Worthy Events

The following log patterns should trigger monitoring alerts:

#### Critical Alerts (Immediate Response)
```python
logger.critical("Database connection lost - system offline")
logger.critical("Sandbox security breach detected")
logger.critical("Configuration corruption detected")
```

#### Warning Alerts (Monitor Closely)  
```python
logger.error("LLM API quota exceeded")
logger.error("Client data parsing failed for %s", client_id)
logger.warning("Memory usage exceeding 80%: %dMB", memory_usage)
```

#### Metric Tracking
```python
logger.info("Performance metric", extra={
    "metric_type": "response_time",
    "value": response_time_ms,
    "endpoint": "llm_request"
})
```

## Troubleshooting Guide

### Common Issues and Solutions

#### Issue: Logs not appearing in files
**Symptoms**: Console output works but files remain empty
**Diagnosis**:
```bash
# Check file permissions
ls -la logs/
# Check disk space  
df -h
# Verify config syntax
python -c "import yaml; yaml.safe_load(open('config/logging_config.yaml'))"
```

**Solutions**:
1. Ensure `logs/` directory is writable
2. Verify sufficient disk space (>100MB recommended)
3. Check YAML syntax in logging_config.yaml
4. Review file handler configuration

#### Issue: Log rotation not working
**Symptoms**: Log files grow beyond configured size limits
**Diagnosis**:
```python
import logging.handlers
handler = logging.handlers.RotatingFileHandler("test.log", maxBytes=1024, backupCount=3)
# Test rotation manually
for i in range(1000):
    handler.emit(logging.LogRecord("test", logging.INFO, "", 0, f"Test message {i}", (), None))
```

**Solutions**:
1. Verify `maxBytes` and `backupCount` settings
2. Check file system permissions for creating `.1`, `.2` backup files
3. Ensure no other processes have files locked
4. Consider using `TimedRotatingFileHandler` for time-based rotation

#### Issue: Performance degradation with high log volume
**Symptoms**: Application slowdown when DEBUG logging enabled
**Diagnosis**:
```python
import time
import logging

# Measure logging overhead
start_time = time.time()
logger = logging.getLogger("test")
for i in range(10000):
    logger.debug("Test message %d", i)
end_time = time.time()
print(f"10k log messages took {end_time - start_time:.2f}s")
```

**Solutions**:
1. Raise log level to INFO or WARNING in production
2. Use lazy evaluation for expensive log message formatting
3. Consider async logging handlers for high throughput
4. Profile and optimize hot code paths generating excessive logs

### Debug Mode Configuration

For intensive debugging sessions, use this configuration:

```yaml
# Debug mode - maximum verbosity
version: 1
disable_existing_loggers: false

formatters:
  debug:
    format: "%(asctime)s.%(msecs)03d [%(process)d:%(thread)d] %(name)s:%(funcName)s:%(lineno)d %(levelname)s - %(message)s"
    datefmt: "%Y-%m-%d %H:%M:%S"

handlers:
  debug_console:
    class: logging.StreamHandler
    level: DEBUG
    formatter: debug
    
  debug_file:
    class: logging.FileHandler
    level: DEBUG  
    formatter: debug
    filename: logs/debug_session.log
    mode: w  # Overwrite on each run

root:
  level: DEBUG
  handlers: [debug_console, debug_file]
```

### Log Analysis Tools

#### Recommended Tools for Log Analysis

1. **Command Line**:
   ```bash
   # Error summary
   grep "ERROR\|CRITICAL" logs/client_activation.log | tail -20
   
   # Client-specific events
   grep "client_id.*ABC123" logs/client_activation.log
   
   # Performance analysis
   grep "Duration:" logs/client_activation.log | awk '{print $NF}' | sort -n
   ```

2. **Log Parsing Script**:
   ```python
   import re
   from collections import Counter
   
   def analyze_logs(log_file):
       with open(log_file) as f:
           lines = f.readlines()
       
       # Count log levels
       levels = Counter()
       for line in lines:
           if match := re.search(r' - (\w+) - ', line):
               levels[match.group(1)] += 1
               
       return levels
   ```

3. **JSON Log Processing** (if using JSON formatter):
   ```python
   import json
   import pandas as pd
   
   def json_logs_to_dataframe(log_file):
       records = []
       with open(log_file) as f:
           for line in f:
               records.append(json.loads(line))
       return pd.DataFrame(records)
   ```

## Security Considerations

### Sensitive Data Handling

1. **Never log sensitive information**:
   ```python
   # Bad - logs sensitive data
   logger.info(f"Processing client: {client_data}")
   
   # Good - logs identifier only
   logger.info("Processing client: %s", client_data.get("id", "unknown"))
   ```

2. **Use log sanitization**:
   ```python
   def sanitize_for_logging(data):
       """Remove or mask sensitive fields before logging."""
       safe_data = data.copy()
       for field in ['password', 'api_key', 'ssn', 'credit_card']:
           if field in safe_data:
               safe_data[field] = "***REDACTED***"
       return safe_data
   ```

3. **Implement log access controls**:
   - Restrict file permissions: `chmod 640 logs/*.log`
   - Use separate log directories for different security levels
   - Implement log rotation with secure deletion

### Compliance Requirements

For environments with compliance requirements (HIPAA, SOC2, etc.):

1. **Audit logging**: Separate audit trail for compliance events
2. **Retention policies**: Configure retention based on regulatory requirements  
3. **Access logging**: Log who accesses what client data when
4. **Tamper detection**: Use checksums or digital signatures for critical logs

## Best Practices Summary

### Development
- Use DEBUG level liberally during development
- Include context in log messages (client_id, workflow_id, etc.)
- Test log configuration changes in development first
- Use structured logging for complex data

### Production  
- Set appropriate log levels (INFO or WARNING for most modules)
- Monitor log file sizes and rotation
- Implement log monitoring and alerting
- Regular log cleanup and archival

### Performance
- Use lazy evaluation for expensive log message formatting
- Consider async handlers for high-volume logging
- Profile logging overhead in performance-critical code
- Monitor disk I/O impact of logging

### Security
- Never log sensitive data (passwords, API keys, PII)
- Implement proper file permissions on log files
- Use log rotation to prevent disk exhaustion attacks
- Consider log encryption for highly sensitive environments

This comprehensive logging system ensures robust monitoring, debugging capabilities, and production readiness for the Client Activation Engine while maintaining security and performance standards.
