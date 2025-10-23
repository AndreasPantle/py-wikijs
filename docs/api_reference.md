# API Reference

Complete reference for the Wiki.js Python SDK.

## Table of Contents

- [Client](#client)
- [Authentication](#authentication)
- [Pages API](#pages-api)
- [Models](#models)
- [Exceptions](#exceptions)
- [Utilities](#utilities)

---

## Client

### WikiJSClient

The main client class for interacting with Wiki.js API.

```python
from wikijs import WikiJSClient

client = WikiJSClient(
    base_url="https://wiki.example.com",
    auth="your-api-key",
    timeout=30,
    verify_ssl=True,
    user_agent="Custom-Agent/1.0"
)
```

#### Parameters

- **base_url** (`str`): The base URL of your Wiki.js instance
- **auth** (`str | AuthHandler`): Authentication (API key string or auth handler)
- **timeout** (`int`, optional): Request timeout in seconds (default: 30)
- **verify_ssl** (`bool`, optional): Whether to verify SSL certificates (default: True)
- **user_agent** (`str`, optional): Custom User-Agent header

#### Methods

##### test_connection()

Test connection to Wiki.js instance.

```python
is_connected = client.test_connection()
```

**Returns:** `bool` - True if connection successful

**Raises:**
- `ConfigurationError`: If client is not properly configured
- `ConnectionError`: If cannot connect to server
- `AuthenticationError`: If authentication fails

##### close()

Close the HTTP session and clean up resources.

```python
client.close()
```

#### Context Manager Support

```python
with WikiJSClient("https://wiki.example.com", auth="api-key") as client:
    pages = client.pages.list()
# Session automatically closed
```

---

## Authentication

### API Key Authentication

```python
from wikijs.auth import APIKeyAuth

auth = APIKeyAuth("your-api-key")
client = WikiJSClient("https://wiki.example.com", auth=auth)
```

### JWT Authentication

JWT authentication uses token-based authentication with automatic refresh capabilities.

```python
from wikijs.auth import JWTAuth

# Initialize with JWT token and refresh token
auth = JWTAuth(
    token="eyJ0eXAiOiJKV1QiLCJhbGc...",
    base_url="https://wiki.example.com",
    refresh_token="refresh_token_here",  # Optional: for automatic token refresh
    expires_at=1234567890  # Optional: Unix timestamp of token expiration
)
client = WikiJSClient("https://wiki.example.com", auth=auth)
```

**Parameters:**
- **token** (`str`): The JWT token string
- **base_url** (`str`): Wiki.js instance URL (needed for token refresh)
- **refresh_token** (`str`, optional): Refresh token for automatic renewal
- **expires_at** (`float`, optional): Token expiration timestamp (Unix timestamp)

**Features:**
- Automatic token expiration detection
- Automatic token refresh when refresh token is provided
- Configurable refresh buffer (default: 5 minutes before expiration)
- Token masking in logs for security

---

## Pages API

Access the Pages API through `client.pages`.

### list()

List pages with optional filtering and pagination.

```python
pages = client.pages.list(
    limit=10,
    offset=0,
    search="query",
    tags=["tag1", "tag2"],
    locale="en",
    author_id=1,
    order_by="title",
    order_direction="ASC"
)
```

#### Parameters

- **limit** (`int`, optional): Maximum number of pages to return
- **offset** (`int`, optional): Number of pages to skip
- **search** (`str`, optional): Search term to filter pages
- **tags** (`List[str]`, optional): List of tags to filter by
- **locale** (`str`, optional): Locale to filter by
- **author_id** (`int`, optional): Author ID to filter by
- **order_by** (`str`, optional): Field to order by (`title`, `created_at`, `updated_at`, `path`)
- **order_direction** (`str`, optional): Order direction (`ASC` or `DESC`)

**Returns:** `List[Page]` - List of Page objects

**Raises:**
- `APIError`: If the API request fails
- `ValidationError`: If parameters are invalid

### get()

Get a specific page by ID.

```python
page = client.pages.get(123)
```

#### Parameters

- **page_id** (`int`): The page ID

**Returns:** `Page` - Page object

**Raises:**
- `APIError`: If the page is not found or request fails
- `ValidationError`: If page_id is invalid

### get_by_path()

Get a page by its path.

```python
page = client.pages.get_by_path("getting-started", locale="en")
```

#### Parameters

- **path** (`str`): The page path
- **locale** (`str`, optional): The page locale (default: "en")

**Returns:** `Page` - Page object

**Raises:**
- `APIError`: If the page is not found or request fails
- `ValidationError`: If path is invalid

### create()

Create a new page.

```python
from wikijs.models import PageCreate

new_page_data = PageCreate(
    title="Getting Started",
    path="getting-started",
    content="# Welcome\n\nThis is your first page!",
    description="Getting started guide",
    tags=["guide", "tutorial"],
    is_published=True
)

created_page = client.pages.create(new_page_data)
```

#### Parameters

- **page_data** (`PageCreate | dict`): Page creation data

**Returns:** `Page` - Created Page object

**Raises:**
- `APIError`: If page creation fails
- `ValidationError`: If page data is invalid

### update()

Update an existing page.

```python
from wikijs.models import PageUpdate

update_data = PageUpdate(
    title="Updated Title",
    content="Updated content",
    tags=["updated"]
)

updated_page = client.pages.update(123, update_data)
```

#### Parameters

- **page_id** (`int`): The page ID
- **page_data** (`PageUpdate | dict`): Page update data

**Returns:** `Page` - Updated Page object

**Raises:**
- `APIError`: If page update fails
- `ValidationError`: If parameters are invalid

### delete()

Delete a page.

```python
success = client.pages.delete(123)
```

#### Parameters

- **page_id** (`int`): The page ID

**Returns:** `bool` - True if deletion was successful

**Raises:**
- `APIError`: If page deletion fails
- `ValidationError`: If page_id is invalid

### search()

Search for pages by content and title.

```python
results = client.pages.search("search query", limit=10)
```

#### Parameters

- **query** (`str`): Search query string
- **limit** (`int`, optional): Maximum number of results to return
- **locale** (`str`, optional): Locale to search in

**Returns:** `List[Page]` - List of matching Page objects

**Raises:**
- `APIError`: If search fails
- `ValidationError`: If parameters are invalid

### get_by_tags()

Get pages by tags.

```python
pages = client.pages.get_by_tags(
    tags=["tutorial", "guide"],
    match_all=True,
    limit=10
)
```

#### Parameters

- **tags** (`List[str]`): List of tags to search for
- **match_all** (`bool`, optional): If True, pages must have ALL tags (default: True)
- **limit** (`int`, optional): Maximum number of results to return

**Returns:** `List[Page]` - List of matching Page objects

**Raises:**
- `APIError`: If request fails
- `ValidationError`: If parameters are invalid

---

## Models

### Page

Represents a Wiki.js page with all metadata and content.

```python
from wikijs.models import Page
```

#### Properties

- **id** (`int`): Unique page identifier
- **title** (`str`): Page title
- **path** (`str`): Page path/slug
- **content** (`str`): Page content
- **description** (`str`, optional): Page description
- **is_published** (`bool`): Whether page is published
- **is_private** (`bool`): Whether page is private
- **tags** (`List[str]`): Page tags
- **locale** (`str`): Page locale
- **author_id** (`int`, optional): Author ID
- **author_name** (`str`, optional): Author name
- **author_email** (`str`, optional): Author email
- **editor** (`str`, optional): Editor used
- **created_at** (`datetime`): Creation timestamp
- **updated_at** (`datetime`): Last update timestamp

#### Computed Properties

```python
# Word count
word_count = page.word_count

# Reading time (minutes)
reading_time = page.reading_time

# Full URL path
url_path = page.url_path
```

#### Methods

```python
# Extract markdown headings
headings = page.extract_headings()

# Check if page has a tag
has_tutorial_tag = page.has_tag("tutorial")
```

### PageCreate

Data model for creating a new page.

```python
from wikijs.models import PageCreate

page_data = PageCreate(
    title="New Page",
    path="new-page",
    content="Page content",
    description="Optional description",
    is_published=True,
    is_private=False,
    tags=["tag1", "tag2"],
    locale="en",
    editor="markdown"
)
```

#### Required Fields

- **title** (`str`): Page title
- **path** (`str`): Page path/slug
- **content** (`str`): Page content

#### Optional Fields

- **description** (`str`): Page description
- **is_published** (`bool`): Whether to publish immediately (default: True)
- **is_private** (`bool`): Whether page should be private (default: False)
- **tags** (`List[str]`): Page tags (default: [])
- **locale** (`str`): Page locale (default: "en")
- **editor** (`str`): Editor to use (default: "markdown")

### PageUpdate

Data model for updating an existing page.

```python
from wikijs.models import PageUpdate

update_data = PageUpdate(
    title="Updated Title",
    content="Updated content",
    tags=["new-tag"]
)
```

#### Optional Fields (all)

- **title** (`str`): Page title
- **content** (`str`): Page content
- **description** (`str`): Page description
- **is_published** (`bool`): Publication status
- **is_private** (`bool`): Privacy status
- **tags** (`List[str]`): Page tags

---

## Exceptions

### APIError

Base exception for API-related errors.

```python
from wikijs.exceptions import APIError

try:
    page = client.pages.get(999)
except APIError as e:
    print(f"API error: {e}")
```

### AuthenticationError

Raised when authentication fails.

```python
from wikijs.exceptions import AuthenticationError

try:
    client.test_connection()
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
```

### ValidationError

Raised when input validation fails.

```python
from wikijs.exceptions import ValidationError

try:
    page_data = PageCreate(title="", path="invalid path")
except ValidationError as e:
    print(f"Validation error: {e}")
```

### ConfigurationError

Raised when client configuration is invalid.

```python
from wikijs.exceptions import ConfigurationError

try:
    client = WikiJSClient("", auth=None)
except ConfigurationError as e:
    print(f"Configuration error: {e}")
```

### ConnectionError

Raised when connection to Wiki.js fails.

```python
from wikijs.exceptions import ConnectionError

try:
    client.test_connection()
except ConnectionError as e:
    print(f"Connection error: {e}")
```

### TimeoutError

Raised when requests timeout.

```python
from wikijs.exceptions import TimeoutError

try:
    pages = client.pages.list()
except TimeoutError as e:
    print(f"Request timed out: {e}")
```

---

## Utilities

### URL Utilities

```python
from wikijs.utils import normalize_url, build_api_url

# Normalize a base URL
normalized = normalize_url("https://wiki.example.com/")

# Build API endpoint URL
api_url = build_api_url("https://wiki.example.com", "/graphql")
```

### Response Utilities

```python
from wikijs.utils import parse_wiki_response, extract_error_message

# Parse Wiki.js API response
data = parse_wiki_response(response_data)

# Extract error message from HTTP response
error_msg = extract_error_message(http_response)
```

---

## Error Handling Best Practices

### Comprehensive Error Handling

```python
from wikijs import WikiJSClient
from wikijs.exceptions import (
    APIError,
    AuthenticationError,
    ValidationError,
    ConnectionError,
    TimeoutError
)

try:
    client = WikiJSClient("https://wiki.example.com", auth="api-key")
    pages = client.pages.list(limit=10)
    
except AuthenticationError:
    print("Invalid API key or authentication failed")
except ValidationError as e:
    print(f"Invalid parameters: {e}")
except ConnectionError:
    print("Cannot connect to Wiki.js instance")
except TimeoutError:
    print("Request timed out")
except APIError as e:
    print(f"API error: {e}")
```

### Retry Logic

```python
import time
from wikijs.exceptions import TimeoutError, ConnectionError

def with_retry(func, max_retries=3, delay=1):
    for attempt in range(max_retries):
        try:
            return func()
        except (TimeoutError, ConnectionError) as e:
            if attempt == max_retries - 1:
                raise
            time.sleep(delay * (2 ** attempt))  # Exponential backoff

# Usage
pages = with_retry(lambda: client.pages.list())
```

---

## Performance Tips

### Connection Reuse

```python
# Use context manager for automatic cleanup
with WikiJSClient("https://wiki.example.com", auth="api-key") as client:
    # Multiple operations reuse the same connection
    pages = client.pages.list()
    page = client.pages.get(123)
    updated = client.pages.update(123, data)
```

### Pagination

```python
# Efficiently paginate through large result sets
def get_all_pages(client, batch_size=50):
    offset = 0
    all_pages = []
    
    while True:
        batch = client.pages.list(limit=batch_size, offset=offset)
        if not batch:
            break
        all_pages.extend(batch)
        offset += batch_size
    
    return all_pages
```

### Filtering

```python
# Use server-side filtering instead of client-side
# Good: Filter on server
tutorial_pages = client.pages.get_by_tags(["tutorial"])

# Better: Combine filters
recent_tutorials = client.pages.list(
    tags=["tutorial"],
    order_by="updated_at",
    order_direction="DESC",
    limit=10
)
```