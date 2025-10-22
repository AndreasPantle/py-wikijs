# Async/Await Support

The Wiki.js Python SDK provides full async/await support for high-performance concurrent operations using `aiohttp`.

## Installation

```bash
pip install wikijs-python-sdk[async]
```

## Quick Start

```python
import asyncio
from wikijs.aio import AsyncWikiJSClient

async def main():
    # Use async context manager for automatic cleanup
    async with AsyncWikiJSClient(
        base_url="https://wiki.example.com",
        auth="your-api-key"
    ) as client:
        # All operations are now async
        pages = await client.pages.list()
        page = await client.pages.get(123)

        print(f"Found {len(pages)} pages")
        print(f"Page title: {page.title}")

# Run the async function
asyncio.run(main())
```

## Why Async?

Async operations provide significant performance benefits for concurrent requests:

- **Sequential (Sync)**: Requests happen one-by-one
  - 100 requests @ 100ms each = 10 seconds

- **Concurrent (Async)**: Requests happen simultaneously
  - 100 requests @ 100ms each = ~100ms total
  - **>3x faster** for typical workloads!

## Basic Operations

### Connection Testing

```python
async with AsyncWikiJSClient(url, auth) as client:
    connected = await client.test_connection()
    print(f"Connected: {connected}")
```

### Listing Pages

```python
# List all pages
pages = await client.pages.list()

# List with filtering
pages = await client.pages.list(
    limit=10,
    offset=0,
    search="documentation",
    locale="en",
    order_by="title",
    order_direction="ASC"
)
```

### Getting Pages

```python
# Get by ID
page = await client.pages.get(123)

# Get by path
page = await client.pages.get_by_path("getting-started")
```

### Creating Pages

```python
from wikijs.models.page import PageCreate

new_page = PageCreate(
    title="New Page",
    path="new-page",
    content="# New Page\n\nContent here.",
    description="A new page",
    tags=["new", "example"]
)

created_page = await client.pages.create(new_page)
print(f"Created page with ID: {created_page.id}")
```

### Updating Pages

```python
from wikijs.models.page import PageUpdate

updates = PageUpdate(
    title="Updated Title",
    content="# Updated\n\nNew content.",
    tags=["updated"]
)

updated_page = await client.pages.update(123, updates)
```

### Deleting Pages

```python
success = await client.pages.delete(123)
print(f"Deleted: {success}")
```

### Searching Pages

```python
results = await client.pages.search("api documentation", limit=10)
for page in results:
    print(f"- {page.title}")
```

## Concurrent Operations

The real power of async is running multiple operations concurrently:

### Fetch Multiple Pages

```python
import asyncio

# Sequential (slow)
pages = []
for page_id in [1, 2, 3, 4, 5]:
    page = await client.pages.get(page_id)
    pages.append(page)

# Concurrent (fast!)
tasks = [client.pages.get(page_id) for page_id in [1, 2, 3, 4, 5]]
pages = await asyncio.gather(*tasks)
```

### Bulk Create Operations

```python
# Create multiple pages concurrently
pages_to_create = [
    PageCreate(title=f"Page {i}", path=f"page-{i}", content=f"Content {i}")
    for i in range(1, 11)
]

tasks = [client.pages.create(page) for page in pages_to_create]
created_pages = await asyncio.gather(*tasks, return_exceptions=True)

# Filter out any errors
successful = [p for p in created_pages if isinstance(p, Page)]
print(f"Created {len(successful)} pages")
```

### Parallel Search Operations

```python
# Search multiple terms concurrently
search_terms = ["api", "guide", "tutorial", "reference"]

tasks = [client.pages.search(term) for term in search_terms]
results = await asyncio.gather(*tasks)

for term, pages in zip(search_terms, results):
    print(f"{term}: {len(pages)} pages found")
```

## Error Handling

Handle errors gracefully with try/except:

```python
from wikijs.exceptions import (
    AuthenticationError,
    NotFoundError,
    APIError
)

async with AsyncWikiJSClient(url, auth) as client:
    try:
        page = await client.pages.get(999)
    except NotFoundError:
        print("Page not found")
    except AuthenticationError:
        print("Invalid API key")
    except APIError as e:
        print(f"API error: {e}")
```

### Handle Errors in Concurrent Operations

```python
# Use return_exceptions=True to continue on errors
tasks = [client.pages.get(page_id) for page_id in [1, 2, 999, 4, 5]]
results = await asyncio.gather(*tasks, return_exceptions=True)

# Process results
for i, result in enumerate(results):
    if isinstance(result, Exception):
        print(f"Page {i}: Error - {result}")
    else:
        print(f"Page {i}: {result.title}")
```

## Resource Management

### Automatic Cleanup with Context Manager

```python
# Recommended: Use async context manager
async with AsyncWikiJSClient(url, auth) as client:
    # Session automatically closed when block exits
    pages = await client.pages.list()
```

### Manual Resource Management

```python
# If you need manual control
client = AsyncWikiJSClient(url, auth)
try:
    pages = await client.pages.list()
finally:
    await client.close()  # Important: close the session
```

## Advanced Configuration

### Custom Connection Pool

```python
import aiohttp

# Create custom connector for fine-tuned control
connector = aiohttp.TCPConnector(
    limit=200,              # Max connections
    limit_per_host=50,      # Max per host
    ttl_dns_cache=600,      # DNS cache TTL
)

async with AsyncWikiJSClient(
    url,
    auth,
    connector=connector
) as client:
    # Use client with custom connector
    pages = await client.pages.list()
```

### Custom Timeout

```python
# Set custom timeout (in seconds)
async with AsyncWikiJSClient(
    url,
    auth,
    timeout=60  # 60 second timeout
) as client:
    pages = await client.pages.list()
```

### Disable SSL Verification (Development Only)

```python
async with AsyncWikiJSClient(
    url,
    auth,
    verify_ssl=False  # NOT recommended for production!
) as client:
    pages = await client.pages.list()
```

## Performance Best Practices

### 1. Use Connection Pooling

The async client automatically uses connection pooling. Keep a single client instance for your application:

```python
# Good: Reuse client
client = AsyncWikiJSClient(url, auth)
for i in range(100):
    await client.pages.get(i)
await client.close()

# Bad: Create new client each time
for i in range(100):
    async with AsyncWikiJSClient(url, auth) as client:
        await client.pages.get(i)  # New connection each time!
```

### 2. Batch Concurrent Operations

Use `asyncio.gather()` for concurrent operations:

```python
# Fetch 100 pages concurrently (fast!)
tasks = [client.pages.get(i) for i in range(1, 101)]
pages = await asyncio.gather(*tasks, return_exceptions=True)
```

### 3. Use Semaphores to Control Concurrency

Limit concurrent connections to avoid overwhelming the server:

```python
import asyncio

async def fetch_page_with_semaphore(client, page_id, sem):
    async with sem:  # Limit concurrent operations
        return await client.pages.get(page_id)

# Limit to 10 concurrent requests
sem = asyncio.Semaphore(10)
tasks = [
    fetch_page_with_semaphore(client, i, sem)
    for i in range(1, 101)
]
pages = await asyncio.gather(*tasks)
```

## Comparison: Sync vs Async

| Feature | Sync Client | Async Client |
|---------|-------------|--------------|
| Import | `from wikijs import WikiJSClient` | `from wikijs.aio import AsyncWikiJSClient` |
| Usage | `client.pages.get(123)` | `await client.pages.get(123)` |
| Context Manager | `with WikiJSClient(...) as client:` | `async with AsyncWikiJSClient(...) as client:` |
| Concurrency | Sequential only | Concurrent with `asyncio.gather()` |
| Performance | Good for single requests | Excellent for multiple requests |
| Dependencies | `requests` | `aiohttp` |
| Best For | Simple scripts, sequential operations | Web apps, high-throughput, concurrent ops |

## When to Use Async

**Use Async When:**
- Making multiple concurrent API calls
- Building async web applications (FastAPI, aiohttp)
- Need maximum throughput
- Working with other async libraries

**Use Sync When:**
- Simple scripts or automation
- Sequential operations only
- Don't need concurrency
- Simpler code is preferred

## Complete Example

```python
import asyncio
from wikijs.aio import AsyncWikiJSClient
from wikijs.models.page import PageCreate, PageUpdate

async def main():
    async with AsyncWikiJSClient(
        base_url="https://wiki.example.com",
        auth="your-api-key"
    ) as client:
        # Test connection
        print("Testing connection...")
        connected = await client.test_connection()
        print(f"Connected: {connected}")

        # Create page
        print("\nCreating page...")
        new_page = PageCreate(
            title="Test Page",
            path="test-page",
            content="# Test\n\nContent here.",
            tags=["test"]
        )
        page = await client.pages.create(new_page)
        print(f"Created page {page.id}: {page.title}")

        # Update page
        print("\nUpdating page...")
        updates = PageUpdate(title="Updated Test Page")
        page = await client.pages.update(page.id, updates)
        print(f"Updated: {page.title}")

        # List pages concurrently
        print("\nFetching multiple pages...")
        tasks = [
            client.pages.list(limit=5),
            client.pages.search("test"),
            client.pages.get_by_tags(["test"])
        ]
        list_results, search_results, tag_results = await asyncio.gather(*tasks)
        print(f"Listed: {len(list_results)}")
        print(f"Searched: {len(search_results)}")
        print(f"By tags: {len(tag_results)}")

        # Clean up
        print("\nDeleting test page...")
        await client.pages.delete(page.id)
        print("Done!")

if __name__ == "__main__":
    asyncio.run(main())
```

## See Also

- [Basic Usage Guide](../README.md#usage)
- [API Reference](api/)
- [Examples](../examples/)
- [Performance Benchmarks](benchmarks.md)
