# Logging Guide

## Overview

The wikijs-python-sdk includes structured logging capabilities for production monitoring and debugging.

## Configuration

### Basic Setup

```python
from wikijs import WikiJSClient
import logging

# Enable debug logging
client = WikiJSClient(
    "https://wiki.example.com",
    auth="your-api-key",
    log_level=logging.DEBUG
)
```

### JSON Logging

```python
from wikijs.logging import setup_logging

# Setup JSON logging to file
logger = setup_logging(
    level=logging.INFO,
    format_type="json",
    output_file="wikijs.log"
)
```

### Text Logging

```python
from wikijs.logging import setup_logging

# Setup text logging to console
logger = setup_logging(
    level=logging.INFO,
    format_type="text"
)
```

## Log Levels

- `DEBUG`: Detailed information for debugging
- `INFO`: General informational messages
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical failures

## Log Fields

JSON logs include:
- `timestamp`: ISO 8601 timestamp
- `level`: Log level
- `message`: Log message
- `module`: Python module
- `function`: Function name
- `line`: Line number
- `extra`: Additional context

## Example Output

```json
{
  "timestamp": "2025-10-23T10:15:30.123456",
  "level": "INFO",
  "logger": "wikijs",
  "message": "Initializing WikiJSClient",
  "module": "client",
  "function": "__init__",
  "line": 45,
  "base_url": "https://wiki.example.com",
  "timeout": 30
}
```

## Best Practices

1. Use appropriate log levels
2. Enable DEBUG only for development
3. Rotate log files in production
4. Monitor error rates
5. Include contextual information
