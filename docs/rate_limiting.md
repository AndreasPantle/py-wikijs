# Rate Limiting Guide

## Overview

The wikijs-python-sdk includes built-in rate limiting to prevent API throttling and ensure stable operation.

## Basic Usage

```python
from wikijs import WikiJSClient

# Create client with rate limiting (10 requests/second)
client = WikiJSClient(
    "https://wiki.example.com",
    auth="your-api-key",
    rate_limit=10.0
)

# API calls will be automatically rate-limited
pages = client.pages.list()  # Throttled if necessary
```

## Configuration

### Global Rate Limit

```python
client = WikiJSClient(
    "https://wiki.example.com",
    auth="your-api-key",
    rate_limit=5.0,  # 5 requests per second
    rate_limit_timeout=60.0  # Wait up to 60 seconds
)
```

### Without Rate Limiting

```python
# Disable rate limiting (use with caution)
client = WikiJSClient(
    "https://wiki.example.com",
    auth="your-api-key",
    rate_limit=None
)
```

## How It Works

The rate limiter uses a **token bucket algorithm**:

1. Tokens refill at a constant rate (requests/second)
2. Each request consumes one token
3. If no tokens available, request waits
4. Burst traffic is supported up to bucket size

## Per-Endpoint Rate Limiting

For advanced use cases:

```python
from wikijs.ratelimit import PerEndpointRateLimiter

limiter = PerEndpointRateLimiter(default_rate=10.0)

# Set custom rate for specific endpoint
limiter.set_limit("/graphql", 5.0)

# Acquire permission
if limiter.acquire("/graphql", timeout=10.0):
    # Make request
    pass
```

## Timeout Handling

```python
from wikijs import WikiJSClient

client = WikiJSClient(
    "https://wiki.example.com",
    auth="your-api-key",
    rate_limit=1.0,
    rate_limit_timeout=5.0
)

try:
    # This may raise TimeoutError if rate limit exceeded
    result = client.pages.list()
except TimeoutError as e:
    print("Rate limit timeout exceeded")
```

## Best Practices

1. **Set appropriate limits**: Match your Wiki.js instance capabilities
2. **Monitor rate limit hits**: Track timeout errors
3. **Use burst capacity**: Allow short bursts of traffic
4. **Implement retry logic**: Handle timeout errors gracefully
5. **Test limits**: Validate under load

## Recommended Limits

- **Development**: 10-20 requests/second
- **Production**: 5-10 requests/second
- **High-volume**: Configure based on Wiki.js capacity
- **Batch operations**: Lower rate (1-2 requests/second)

## Example: Batch Processing

```python
from wikijs import WikiJSClient
import time

client = WikiJSClient(
    "https://wiki.example.com",
    auth="your-api-key",
    rate_limit=2.0  # Conservative rate for batch
)

page_ids = range(1, 101)
results = []

for page_id in page_ids:
    try:
        page = client.pages.get(page_id)
        results.append(page)
    except TimeoutError:
        print(f"Rate limit timeout for page {page_id}")
    except Exception as e:
        print(f"Error processing page {page_id}: {e}")

print(f"Processed {len(results)} pages")
```

## Monitoring

Combine with metrics to track rate limiting impact:

```python
metrics = client.get_metrics()
print(f"Requests: {metrics['total_requests']}")
print(f"Avg latency: {metrics['latency']['avg']}")
# Increased latency may indicate rate limiting
```
