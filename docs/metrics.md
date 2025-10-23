# Metrics and Telemetry Guide

## Overview

The wikijs-python-sdk includes built-in metrics collection for monitoring performance and reliability.

## Basic Usage

```python
from wikijs import WikiJSClient

# Create client with metrics enabled (default)
client = WikiJSClient(
    "https://wiki.example.com",
    auth="your-api-key",
    enable_metrics=True
)

# Perform operations
pages = client.pages.list()
page = client.pages.get(123)

# Get metrics
metrics = client.get_metrics()
print(f"Total requests: {metrics['total_requests']}")
print(f"Error rate: {metrics['error_rate']:.2f}%")
print(f"Avg latency: {metrics['latency']['avg']:.2f}ms")
print(f"P95 latency: {metrics['latency']['p95']:.2f}ms")
```

## Available Metrics

### Counters
- `total_requests`: Total API requests made
- `total_errors`: Total errors (4xx, 5xx responses)
- `total_server_errors`: Server errors (5xx responses)

### Latency Statistics
- `min`: Minimum request duration
- `max`: Maximum request duration
- `avg`: Average request duration
- `p50`: 50th percentile (median)
- `p95`: 95th percentile
- `p99`: 99th percentile

### Error Rate
- Percentage of failed requests

## Example Output

```python
{
    "total_requests": 150,
    "total_errors": 3,
    "error_rate": 2.0,
    "latency": {
        "min": 45.2,
        "max": 523.8,
        "avg": 127.3,
        "p50": 98.5,
        "p95": 312.7,
        "p99": 487.2
    },
    "counters": {
        "total_requests": 150,
        "total_errors": 3,
        "total_server_errors": 1
    },
    "gauges": {}
}
```

## Advanced Usage

### Custom Metrics

```python
from wikijs.metrics import get_metrics

metrics = get_metrics()

# Increment custom counter
metrics.increment("custom_operation_count", 5)

# Set gauge value
metrics.set_gauge("cache_hit_rate", 87.5)

# Get statistics
stats = metrics.get_stats()
```

### Reset Metrics

```python
metrics = get_metrics()
metrics.reset()
```

## Monitoring Integration

Metrics can be exported to monitoring systems:

```python
import json

# Export metrics as JSON
metrics_json = json.dumps(client.get_metrics())

# Send to monitoring service
# send_to_datadog(metrics_json)
# send_to_prometheus(metrics_json)
```

## Best Practices

1. Monitor error rates regularly
2. Set up alerts for high latency (p95 > threshold)
3. Track trends over time
4. Reset metrics periodically
5. Export to external monitoring systems
