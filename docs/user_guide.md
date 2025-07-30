# User Guide

Complete guide to using the Wiki.js Python SDK for common tasks and workflows.

## Table of Contents

- [Getting Started](#getting-started)
- [Authentication](#authentication)
- [Working with Pages](#working-with-pages)
- [Advanced Features](#advanced-features)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)

---

## Getting Started

### Installation

```bash
pip install wikijs-python-sdk
```

### Basic Setup

```python
from wikijs import WikiJSClient

# Initialize the client
client = WikiJSClient(
    base_url="https://your-wiki.example.com",
    auth="your-api-key"
)

# Test the connection
if client.test_connection():
    print("Connected successfully!")
else:
    print("Connection failed")
```

### Your First API Call

```python
# Get all pages
pages = client.pages.list()
print(f"Found {len(pages)} pages")

# Get a specific page
page = client.pages.get(1)
print(f"Page title: {page.title}")
```

---

## Authentication

### API Key Authentication

The simplest way to authenticate is with an API key:

```python
from wikijs import WikiJSClient

client = WikiJSClient(
    base_url="https://wiki.example.com",
    auth="your-api-key-here"
)
```

**Getting an API Key:**
1. Log into your Wiki.js admin panel
2. Go to Administration → API Keys
3. Create a new API key with appropriate permissions
4. Copy the generated key

### JWT Authentication

For username/password authentication:

```python
from wikijs import WikiJSClient
from wikijs.auth import JWTAuth

auth = JWTAuth(
    username="your-username",
    password="your-password"
)

client = WikiJSClient(
    base_url="https://wiki.example.com",
    auth=auth
)
```

### Custom Authentication

You can also create custom authentication handlers:

```python
from wikijs.auth import AuthHandler

class CustomAuth(AuthHandler):
    def __init__(self, token):
        self.token = token
    
    def get_headers(self):
        return {"Authorization": f"Bearer {self.token}"}
    
    def validate_credentials(self):
        if not self.token:
            raise ValueError("Token is required")

client = WikiJSClient(
    base_url="https://wiki.example.com",
    auth=CustomAuth("your-custom-token")
)
```

---

## Working with Pages

### Listing Pages

#### Basic Listing

```python
# Get all pages
all_pages = client.pages.list()

# Get first 10 pages
first_10 = client.pages.list(limit=10)

# Get pages 11-20 (pagination)
next_10 = client.pages.list(limit=10, offset=10)
```

#### Filtering and Searching

```python
# Search by content
search_results = client.pages.search("getting started")

# Filter by tags
tutorial_pages = client.pages.get_by_tags(["tutorial", "guide"])

# Filter by author
author_pages = client.pages.list(author_id=1)

# Filter by locale
french_pages = client.pages.list(locale="fr")
```

#### Sorting

```python
# Sort by title (A-Z)
pages_by_title = client.pages.list(
    order_by="title",
    order_direction="ASC"
)

# Sort by most recently updated
recent_pages = client.pages.list(
    order_by="updated_at",
    order_direction="DESC",
    limit=10
)

# Sort by creation date (oldest first)
oldest_pages = client.pages.list(
    order_by="created_at",
    order_direction="ASC"
)
```

### Getting Individual Pages

#### By ID

```python
# Get page with ID 123
page = client.pages.get(123)
print(f"Title: {page.title}")
print(f"Content: {page.content}")
```

#### By Path

```python
# Get page by its path
page = client.pages.get_by_path("getting-started")

# Get page in specific locale
french_page = client.pages.get_by_path("guide-utilisateur", locale="fr")
```

### Creating Pages

#### Basic Page Creation

```python
from wikijs.models import PageCreate

# Create a simple page
new_page = PageCreate(
    title="My New Page",
    path="my-new-page",
    content="# Welcome\n\nThis is my new page content!"
)

created_page = client.pages.create(new_page)
print(f"Created page with ID: {created_page.id}")
```

#### Advanced Page Creation

```python
from wikijs.models import PageCreate

# Create a comprehensive page
new_page = PageCreate(
    title="Complete Guide to Wiki.js",
    path="guides/wikijs-complete-guide",
    content="""# Complete Guide to Wiki.js

## Introduction

This guide covers everything you need to know about Wiki.js.

## Getting Started

1. Installation
2. Configuration
3. First steps

## Advanced Topics

- Custom themes
- Plugin development
- API integration
""",
    description="A comprehensive guide covering all aspects of Wiki.js",
    tags=["guide", "tutorial", "wikijs", "documentation"],
    is_published=True,
    is_private=False,
    locale="en",
    editor="markdown"
)

created_page = client.pages.create(new_page)
```

#### Creating from Dictionary

```python
# You can also use a dictionary
page_data = {
    "title": "Quick Note",
    "path": "quick-note",
    "content": "This is a quick note.",
    "tags": ["note", "quick"]
}

created_page = client.pages.create(page_data)
```

### Updating Pages

#### Partial Updates

```python
from wikijs.models import PageUpdate

# Update only specific fields
update_data = PageUpdate(
    title="Updated Title",
    tags=["updated", "modified"]
)

updated_page = client.pages.update(123, update_data)
```

#### Full Content Update

```python
from wikijs.models import PageUpdate

# Update content and metadata
update_data = PageUpdate(
    title="Revised Guide",
    content="""# Revised Guide

This guide has been completely updated with new information.

## What's New

- Updated examples
- New best practices
- Latest features

## Migration Guide

If you're upgrading from the previous version...
""",
    description="Updated guide with latest information",
    tags=["guide", "updated", "v2"],
    is_published=True
)

updated_page = client.pages.update(123, update_data)
```

### Deleting Pages

```python
# Delete a page by ID
success = client.pages.delete(123)
if success:
    print("Page deleted successfully")
else:
    print("Failed to delete page")
```

**⚠️ Warning:** Page deletion is permanent and cannot be undone!

---

## Advanced Features

### Working with Page Metadata

```python
# Get a page
page = client.pages.get(123)

# Access metadata
print(f"Word count: {page.word_count}")
print(f"Reading time: {page.reading_time} minutes")
print(f"Author: {page.author_name}")
print(f"Created: {page.created_at}")
print(f"Last updated: {page.updated_at}")

# Check tags
if page.has_tag("tutorial"):
    print("This is a tutorial page")

# Extract headings
headings = page.extract_headings()
print("Page structure:")
for heading in headings:
    print(f"- {heading}")
```

### Batch Operations

#### Creating Multiple Pages

```python
from wikijs.models import PageCreate

# Prepare multiple pages
pages_to_create = [
    PageCreate(
        title=f"Chapter {i}",
        path=f"guide/chapter-{i}",
        content=f"# Chapter {i}\n\nContent for chapter {i}",
        tags=["guide", f"chapter-{i}"]
    )
    for i in range(1, 6)
]

# Create them one by one
created_pages = []
for page_data in pages_to_create:
    try:
        created_page = client.pages.create(page_data)
        created_pages.append(created_page)
        print(f"Created: {created_page.title}")
    except Exception as e:
        print(f"Failed to create page: {e}")

print(f"Successfully created {len(created_pages)} pages")
```

#### Bulk Updates

```python
from wikijs.models import PageUpdate

# Get pages to update
tutorial_pages = client.pages.get_by_tags(["tutorial"])

# Update all tutorial pages
update_data = PageUpdate(
    tags=["tutorial", "updated-2024"]
)

updated_count = 0
for page in tutorial_pages:
    try:
        client.pages.update(page.id, update_data)
        updated_count += 1
    except Exception as e:
        print(f"Failed to update page {page.id}: {e}")

print(f"Updated {updated_count} tutorial pages")
```

### Content Migration

```python
def migrate_content_format(page):
    """Convert old format to new format."""
    old_content = page.content
    
    # Example: Convert old-style headers
    new_content = old_content.replace("==", "##")
    new_content = new_content.replace("===", "###")
    
    return new_content

# Get pages to migrate
pages_to_migrate = client.pages.list(search="old-format")

for page in pages_to_migrate:
    try:
        new_content = migrate_content_format(page)
        
        update_data = PageUpdate(
            content=new_content,
            tags=page.tags + ["migrated"]
        )
        
        client.pages.update(page.id, update_data)
        print(f"Migrated: {page.title}")
        
    except Exception as e:
        print(f"Failed to migrate {page.title}: {e}")
```

### Template System

```python
from wikijs.models import PageCreate

def create_from_template(title, path, template_data):
    """Create a page from a template."""
    
    # Define templates
    templates = {
        "meeting_notes": """# {meeting_title}

**Date:** {date}
**Attendees:** {attendees}

## Agenda
{agenda}

## Discussion Points
{discussion}

## Action Items
{actions}

## Next Meeting
{next_meeting}
""",
        "project_doc": """# {project_name}

## Overview
{overview}

## Requirements
{requirements}

## Timeline
{timeline}

## Resources
{resources}

## Status
- [ ] Planning
- [ ] Development  
- [ ] Testing
- [ ] Deployment
"""
    }
    
    template = templates.get(template_data["template_type"])
    if not template:
        raise ValueError(f"Unknown template: {template_data['template_type']}")
    
    # Format template
    content = template.format(**template_data)
    
    # Create page
    page_data = PageCreate(
        title=title,
        path=path,
        content=content,
        tags=template_data.get("tags", [])
    )
    
    return client.pages.create(page_data)

# Use template
meeting_page = create_from_template(
    title="Weekly Team Meeting - Jan 15",
    path="meetings/2024-01-15-weekly",
    template_data={
        "template_type": "meeting_notes",
        "meeting_title": "Weekly Team Meeting",
        "date": "January 15, 2024",
        "attendees": "Alice, Bob, Charlie",
        "agenda": "- Project updates\n- Q1 planning\n- Process improvements",
        "discussion": "TBD",
        "actions": "TBD",
        "next_meeting": "January 22, 2024",
        "tags": ["meeting", "weekly", "team"]
    }
)
```

---

## Best Practices

### Error Handling

```python
from wikijs.exceptions import (
    APIError,
    AuthenticationError,
    ValidationError,
    ConnectionError,
    TimeoutError
)

def safe_page_operation(operation_func):
    """Wrapper for safe page operations with proper error handling."""
    try:
        return operation_func()
    except AuthenticationError:
        print("❌ Authentication failed. Check your API key.")
        return None
    except ValidationError as e:
        print(f"❌ Invalid input: {e}")
        return None
    except ConnectionError:
        print("❌ Cannot connect to Wiki.js. Check your URL and network.")
        return None
    except TimeoutError:
        print("❌ Request timed out. Try again later.")
        return None
    except APIError as e:
        print(f"❌ API error: {e}")
        return None

# Usage
result = safe_page_operation(lambda: client.pages.get(123))
if result:
    print(f"✅ Got page: {result.title}")
```

### Resource Management

```python
# Always use context managers for automatic cleanup
with WikiJSClient("https://wiki.example.com", auth="api-key") as client:
    # Do your work here
    pages = client.pages.list()
    # Connection automatically closed when exiting the block

# Or manually manage resources
client = WikiJSClient("https://wiki.example.com", auth="api-key")
try:
    pages = client.pages.list()
finally:
    client.close()  # Always close when done
```

### Configuration Management

```python
import os
from wikijs import WikiJSClient

# Use environment variables for configuration
def create_client():
    """Create a properly configured client from environment variables."""
    base_url = os.getenv("WIKIJS_URL")
    api_key = os.getenv("WIKIJS_API_KEY")
    
    if not base_url or not api_key:
        raise ValueError("WIKIJS_URL and WIKIJS_API_KEY environment variables are required")
    
    return WikiJSClient(
        base_url=base_url,
        auth=api_key,
        timeout=int(os.getenv("WIKIJS_TIMEOUT", "30")),
        verify_ssl=os.getenv("WIKIJS_VERIFY_SSL", "true").lower() == "true"
    )

# Usage
client = create_client()
```

### Logging

```python
import logging
from wikijs import WikiJSClient

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_page_with_logging(client, page_data):
    """Create a page with proper logging."""
    logger.info(f"Creating page: {page_data.title}")
    
    try:
        created_page = client.pages.create(page_data)
        logger.info(f"Successfully created page with ID: {created_page.id}")
        return created_page
    except Exception as e:
        logger.error(f"Failed to create page '{page_data.title}': {e}")
        raise

# Usage
with WikiJSClient("https://wiki.example.com", auth="api-key") as client:
    page_data = PageCreate(
        title="Logged Page",
        path="logged-page",
        content="This creation is logged."
    )
    create_page_with_logging(client, page_data)
```

### Performance Optimization

```python
# Efficient pagination
def get_all_pages_efficiently(client, batch_size=100):
    """Get all pages with efficient pagination."""
    all_pages = []
    offset = 0
    
    while True:
        # Get a batch
        batch = client.pages.list(limit=batch_size, offset=offset)
        
        if not batch:
            break  # No more pages
        
        all_pages.extend(batch)
        offset += batch_size
        
        # Optional: Add a small delay to be nice to the server
        # time.sleep(0.1)
    
    return all_pages

# Use server-side filtering
def get_recent_tutorials(client, days=30):
    """Get recent tutorial pages efficiently."""
    from datetime import datetime, timedelta
    
    # Let the server do the filtering
    pages = client.pages.get_by_tags(["tutorial"])
    
    # Only filter by date client-side if necessary
    cutoff_date = datetime.now() - timedelta(days=days)
    recent_pages = [
        page for page in pages 
        if page.updated_at > cutoff_date
    ]
    
    return recent_pages
```

---

## Troubleshooting

### Common Issues

#### Authentication Problems

```python
# Test your authentication
try:
    client = WikiJSClient("https://wiki.example.com", auth="your-api-key")
    if client.test_connection():
        print("✅ Authentication successful")
    else:
        print("❌ Authentication failed")
except AuthenticationError as e:
    print(f"❌ Authentication error: {e}")
    print("💡 Check your API key and permissions")
```

#### Connection Issues

```python
# Test connection with detailed error info
try:
    client = WikiJSClient("https://wiki.example.com", auth="api-key")
    client.test_connection()
except ConnectionError as e:
    print(f"❌ Connection failed: {e}")
    print("💡 Possible solutions:")
    print("   - Check if the URL is correct")
    print("   - Verify the server is running")
    print("   - Check your network connection")
    print("   - Try with verify_ssl=False if using self-signed certificates")
```

#### SSL Certificate Issues

```python
# For development or self-signed certificates
client = WikiJSClient(
    base_url="https://wiki.example.com",
    auth="api-key",
    verify_ssl=False  # Only for development!
)
```

#### Timeout Issues

```python
# Increase timeout for slow connections
client = WikiJSClient(
    base_url="https://wiki.example.com",
    auth="api-key",
    timeout=60  # 60 seconds
)
```

### Debugging

#### Enable Debug Logging

```python
import logging

# Enable debug logging for the wikijs library
logging.getLogger('wikijs').setLevel(logging.DEBUG)
logging.getLogger('urllib3').setLevel(logging.DEBUG)

# Enable debug logging for requests
logging.basicConfig(level=logging.DEBUG)
```

#### Inspect Raw Responses

```python
# You can inspect the raw HTTP responses for debugging
import requests

# Make a manual request to see the raw response
response = requests.get(
    "https://wiki.example.com/graphql",
    headers={"Authorization": "Bearer your-api-key"},
    json={"query": "{ pages { id title } }"}
)

print(f"Status: {response.status_code}")
print(f"Headers: {response.headers}")
print(f"Content: {response.text}")
```

### Getting Help

If you encounter issues:

1. **Check the logs** - Enable debug logging to see what's happening
2. **Verify your setup** - Ensure URL, credentials, and network connectivity
3. **Check the Wiki.js server** - Look at server logs for errors
4. **Test with curl** - Verify the API works outside of Python
5. **Create an issue** - Report bugs on the GitHub repository

#### Testing with curl

```bash
# Test your Wiki.js GraphQL endpoint
curl -X POST https://wiki.example.com/graphql \
  -H "Authorization: Bearer your-api-key" \
  -H "Content-Type: application/json" \
  -d '{"query": "{ pages { id title } }"}'
```

---

## Next Steps

- Explore the [API Reference](api_reference.md) for detailed information
- Check out the [Examples](../examples/) directory for more code samples
- Read the [Contributing Guide](CONTRIBUTING.md) to help improve the SDK
- Visit the [Wiki.js documentation](https://docs.js.wiki/) to learn more about the platform