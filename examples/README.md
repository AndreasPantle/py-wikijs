# Examples

This directory contains practical examples demonstrating how to use the Wiki.js Python SDK for various tasks.

## 📁 Example Files

### [`basic_usage.py`](basic_usage.py)
**Getting Started Examples**

Demonstrates fundamental operations:
- Connecting to Wiki.js
- Listing and searching pages
- Creating, updating, and deleting pages
- Working with page metadata and tags
- Basic error handling

**Usage:**
```bash
export WIKIJS_URL='https://your-wiki.example.com'
export WIKIJS_API_KEY='your-api-key'
python examples/basic_usage.py
```

### [`content_management.py`](content_management.py)
**Advanced Content Management**

Shows advanced content operations:
- Template-based page creation
- Bulk operations and batch processing
- Content migration and format conversion
- Content auditing and analysis
- Automated content updates

**Usage:**
```bash
export WIKIJS_URL='https://your-wiki.example.com'
export WIKIJS_API_KEY='your-api-key'
python examples/content_management.py
```

## 🚀 Quick Start

1. **Set up your environment:**
   ```bash
   # Clone the repository
   git clone https://github.com/yourusername/wikijs-python-sdk
   cd wikijs-python-sdk
   
   # Install the SDK
   pip install -e .
   
   # Set environment variables
   export WIKIJS_URL='https://your-wiki.example.com'
   export WIKIJS_API_KEY='your-api-key'
   ```

2. **Get your API key:**
   - Log into your Wiki.js admin panel
   - Go to Administration → API Keys
   - Create a new API key with appropriate permissions
   - Copy the generated key

3. **Run an example:**
   ```bash
   python examples/basic_usage.py
   ```

## 📋 Example Scenarios

### Content Creation Workflows

```python
from wikijs import WikiJSClient
from wikijs.models import PageCreate

# Template-based page creation
def create_meeting_notes(client, meeting_data):
    content = f"""# {meeting_data['title']}

**Date:** {meeting_data['date']}
**Attendees:** {', '.join(meeting_data['attendees'])}

## Agenda
{meeting_data['agenda']}

## Action Items
{meeting_data['actions']}
"""
    
    page_data = PageCreate(
        title=meeting_data['title'],
        path=f"meetings/{meeting_data['date']}-{meeting_data['slug']}",
        content=content,
        tags=['meeting'] + meeting_data.get('tags', [])
    )
    
    return client.pages.create(page_data)
```

### Content Analysis

```python
def analyze_wiki_health(client):
    """Analyze wiki content health metrics."""
    
    pages = client.pages.list()
    
    # Calculate metrics
    total_pages = len(pages)
    published_pages = len([p for p in pages if p.is_published])
    tagged_pages = len([p for p in pages if p.tags])
    
    # Word count analysis
    word_counts = [p.word_count for p in pages]
    avg_words = sum(word_counts) / len(word_counts) if word_counts else 0
    
    return {
        'total_pages': total_pages,
        'published_ratio': published_pages / total_pages,
        'tagged_ratio': tagged_pages / total_pages,
        'avg_word_count': avg_words
    }
```

### Batch Operations

```python
def bulk_update_tags(client, search_term, new_tags):
    """Add tags to pages matching a search term."""
    
    pages = client.pages.search(search_term)
    updated_count = 0
    
    for page in pages:
        try:
            # Merge existing and new tags
            updated_tags = list(set(page.tags + new_tags))
            
            update_data = PageUpdate(tags=updated_tags)
            client.pages.update(page.id, update_data)
            updated_count += 1
            
        except Exception as e:
            print(f"Failed to update {page.title}: {e}")
    
    return updated_count
```

## 🛠️ Development Examples

### Custom Authentication

```python
from wikijs.auth import AuthHandler

class CustomAuth(AuthHandler):
    """Custom authentication handler example."""
    
    def __init__(self, custom_token):
        self.token = custom_token
    
    def get_headers(self):
        return {
            'Authorization': f'Custom {self.token}',
            'X-Custom-Header': 'MyApp/1.0'
        }
    
    def validate_credentials(self):
        if not self.token:
            raise ValueError("Custom token is required")

# Usage
client = WikiJSClient(
    base_url="https://wiki.example.com",
    auth=CustomAuth("your-custom-token")
)
```

### Error Handling Patterns

```python
from wikijs.exceptions import (
    APIError, AuthenticationError, ValidationError,
    ConnectionError, TimeoutError
)

def robust_page_operation(client, operation_func):
    """Wrapper for robust page operations with retry logic."""
    
    max_retries = 3
    retry_delay = 1
    
    for attempt in range(max_retries):
        try:
            return operation_func()
            
        except (ConnectionError, TimeoutError) as e:
            if attempt == max_retries - 1:
                raise
            print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
            time.sleep(retry_delay * (2 ** attempt))
            
        except AuthenticationError:
            print("Authentication failed. Check your API key.")
            raise
            
        except ValidationError as e:
            print(f"Invalid input: {e}")
            raise
            
        except APIError as e:
            print(f"API error: {e}")
            raise

# Usage
result = robust_page_operation(
    client,
    lambda: client.pages.get(123)
)
```

## 🔧 Configuration Examples

### Environment-based Configuration

```python
import os
from wikijs import WikiJSClient

def create_client_from_env():
    """Create client from environment variables."""
    
    config = {
        'base_url': os.getenv('WIKIJS_URL'),
        'auth': os.getenv('WIKIJS_API_KEY'),
        'timeout': int(os.getenv('WIKIJS_TIMEOUT', '30')),
        'verify_ssl': os.getenv('WIKIJS_VERIFY_SSL', 'true').lower() == 'true'
    }
    
    # Validate required settings
    if not config['base_url'] or not config['auth']:
        raise ValueError("WIKIJS_URL and WIKIJS_API_KEY are required")
    
    return WikiJSClient(**config)
```

### Configuration File

```python
import json
from wikijs import WikiJSClient

def create_client_from_file(config_file='config.json'):
    """Create client from configuration file."""
    
    with open(config_file, 'r') as f:
        config = json.load(f)
    
    return WikiJSClient(
        base_url=config['wikijs']['url'],
        auth=config['wikijs']['api_key'],
        timeout=config.get('timeout', 30),
        verify_ssl=config.get('verify_ssl', True)
    )

# config.json example:
# {
#   "wikijs": {
#     "url": "https://wiki.example.com",
#     "api_key": "your-api-key"
#   },
#   "timeout": 45,
#   "verify_ssl": true
# }
```

## 📚 Additional Resources

- **[API Reference](../docs/api_reference.md)** - Complete API documentation
- **[User Guide](../docs/user_guide.md)** - Comprehensive usage guide
- **[Contributing](../docs/CONTRIBUTING.md)** - How to contribute to the project
- **[Wiki.js Documentation](https://docs.js.wiki/)** - Official Wiki.js documentation

## 💡 Tips for Success

1. **Always use context managers** for automatic resource cleanup
2. **Handle exceptions appropriately** for robust applications
3. **Use environment variables** for configuration
4. **Test your code** with different scenarios
5. **Be respectful** of the Wiki.js server (don't overwhelm with requests)
6. **Keep your API key secure** and never commit it to version control

## 🆘 Getting Help

If you encounter issues with these examples:

1. **Check your configuration** - Ensure URL and API key are correct
2. **Verify connectivity** - Test that you can reach the Wiki.js instance
3. **Check permissions** - Ensure your API key has necessary permissions
4. **Enable debug logging** - Use logging to see what's happening
5. **Create an issue** - Report bugs or request help on GitHub

---

**Happy coding! 🚀**