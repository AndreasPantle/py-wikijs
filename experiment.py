#!/usr/bin/env python3
"""
Wiki.js Python SDK Experimentation Script

This interactive script lets you experiment with the SDK features in a safe,
mocked environment. Perfect for learning how the SDK works without needing
a real Wiki.js instance.

Usage:
    python experiment.py

The script will guide you through different SDK features and let you
try them out interactively.
"""

import json
import sys
from datetime import datetime
from unittest.mock import Mock, patch

# Import SDK components
from wikijs import WikiJSClient
from wikijs.models import PageCreate, PageUpdate, Page
from wikijs.auth import APIKeyAuth, JWTAuth, NoAuth
from wikijs.exceptions import APIError, ValidationError, NotFoundError


class Colors:
    """ANSI color codes for pretty output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def print_header(text):
    """Print a colored header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(60)}{Colors.END}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*60}{Colors.END}\n")


def print_success(text):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_info(text):
    """Print info message."""
    print(f"{Colors.CYAN}ℹ️  {text}{Colors.END}")


def print_warning(text):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_error(text):
    """Print error message."""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_code(code):
    """Print code snippet."""
    print(f"{Colors.BLUE}{code}{Colors.END}")


def wait_for_enter(prompt="Press Enter to continue..."):
    """Wait for user input."""
    input(f"\n{Colors.YELLOW}{prompt}{Colors.END}")


def setup_mock_session():
    """Set up a mock session for API calls."""
    mock_session = Mock()
    
    # Sample pages data
    sample_pages = [
        {
            "id": 1,
            "title": "Welcome to Wiki.js",
            "path": "home",
            "content": "# Welcome!\n\nThis is your wiki home page.",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-01T12:00:00Z",
            "is_published": True,
            "tags": ["welcome", "home"]
        },
        {
            "id": 2,
            "title": "Getting Started Guide",
            "path": "getting-started",
            "content": "# Getting Started\n\nLearn how to use this wiki effectively.",
            "created_at": "2023-01-02T00:00:00Z",
            "updated_at": "2023-01-02T10:00:00Z",
            "is_published": True,
            "tags": ["guide", "tutorial"]
        },
        {
            "id": 3,
            "title": "API Documentation",
            "path": "api-docs",
            "content": "# API Documentation\n\nComplete API reference.",
            "created_at": "2023-01-03T00:00:00Z",
            "updated_at": "2023-01-03T14:00:00Z",
            "is_published": False,
            "tags": ["api", "documentation"]
        }
    ]
    
    def mock_request(method, url, **kwargs):
        """Mock HTTP request handler."""
        response = Mock()
        response.ok = True
        response.status_code = 200
        
        # Simulate different API endpoints
        if "pages" in url and method.upper() == "GET":
            if url.endswith("/pages"):
                # List pages
                response.json.return_value = {"data": {"pages": sample_pages}}
            else:
                # Get specific page
                page_id = int(url.split("/")[-1]) if url.split("/")[-1].isdigit() else 1
                page = next((p for p in sample_pages if p["id"] == page_id), sample_pages[0])
                response.json.return_value = page
        
        elif "pages" in url and method.upper() == "POST":
            # Create page
            new_page = {
                "id": len(sample_pages) + 1,
                "title": kwargs.get("json", {}).get("title", "New Page"),
                "path": kwargs.get("json", {}).get("path", "new-page"),
                "content": kwargs.get("json", {}).get("content", ""),
                "created_at": datetime.now().isoformat() + "Z",
                "updated_at": datetime.now().isoformat() + "Z",
                "is_published": kwargs.get("json", {}).get("is_published", True),
                "tags": kwargs.get("json", {}).get("tags", [])
            }
            sample_pages.append(new_page)
            response.json.return_value = new_page
            response.status_code = 201
        
        elif "pages" in url and method.upper() == "PUT":
            # Update page
            page_id = int(url.split("/")[-1]) if url.split("/")[-1].isdigit() else 1
            page = next((p for p in sample_pages if p["id"] == page_id), sample_pages[0])
            
            # Update fields from request
            update_data = kwargs.get("json", {})
            for key, value in update_data.items():
                if key in page:
                    page[key] = value
            page["updated_at"] = datetime.now().isoformat() + "Z"
            
            response.json.return_value = page
        
        elif "pages" in url and method.upper() == "DELETE":
            # Delete page
            page_id = int(url.split("/")[-1]) if url.split("/")[-1].isdigit() else 1
            sample_pages[:] = [p for p in sample_pages if p["id"] != page_id]
            response.json.return_value = {"success": True}
            response.status_code = 204
        
        else:
            # Default response
            response.json.return_value = {"message": "Success"}
        
        return response
    
    mock_session.request.side_effect = mock_request
    return mock_session


def experiment_client_setup():
    """Experiment with client setup."""
    print_header("🔧 CLIENT SETUP EXPERIMENT")
    
    print_info("Let's create different types of Wiki.js clients!")
    
    print("\n1. Creating a client with API key authentication:")
    print_code("client = WikiJSClient('https://wiki.example.com', auth='your-api-key')")
    
    try:
        client = WikiJSClient('https://wiki.example.com', auth='demo-api-key-12345')
        print_success(f"Client created! Base URL: {client.base_url}")
        print_info(f"Auth type: {type(client._auth_handler).__name__}")
    except Exception as e:
        print_error(f"Error creating client: {e}")
    
    wait_for_enter()
    
    print("\n2. Creating a client with JWT authentication:")
    print_code("jwt_token = 'eyJ0eXAiOiJKV1Q...'")
    print_code("jwt_auth = JWTAuth(jwt_token)")
    print_code("client = WikiJSClient('https://wiki.example.com', auth=jwt_auth)")
    
    try:
        jwt_token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"
        jwt_auth = JWTAuth(jwt_token)
        jwt_client = WikiJSClient('https://wiki.example.com', auth=jwt_auth)
        print_success("JWT client created successfully!")
        print_info(f"Token preview: {jwt_auth.token_preview}")
    except Exception as e:
        print_error(f"Error creating JWT client: {e}")
    
    wait_for_enter()
    
    print("\n3. URL normalization demo:")
    test_urls = [
        "wiki.example.com",
        "https://wiki.example.com/",
        "http://localhost:3000///",
        "wiki.company.internal:8080"
    ]
    
    for url in test_urls:
        try:
            client = WikiJSClient(url, auth='test-key')
            print_success(f"'{url}' → '{client.base_url}'")
        except Exception as e:
            print_error(f"'{url}' → Error: {e}")
    
    return client


def experiment_data_models():
    """Experiment with data models."""
    print_header("📋 DATA MODELS EXPERIMENT")
    
    print_info("Let's create and manipulate Wiki.js data models!")
    
    print("\n1. Creating a new page:")
    print_code("""
page_data = PageCreate(
    title="My Awesome Page",
    path="awesome-page",
    content="# Welcome\\n\\nThis is **awesome** content!",
    tags=["awesome", "demo"],
    is_published=True
)""")
    
    try:
        page_data = PageCreate(
            title="My Awesome Page",
            path="awesome-page", 
            content="# Welcome\n\nThis is **awesome** content!",
            tags=["awesome", "demo"],
            is_published=True
        )
        print_success("PageCreate model created!")
        print_info(f"Title: {page_data.title}")
        print_info(f"Path: {page_data.path}")
        print_info(f"Tags: {page_data.tags}")
    except Exception as e:
        print_error(f"Error creating page model: {e}")
    
    wait_for_enter()
    
    print("\n2. Model serialization:")
    print_code("page_dict = page_data.to_dict()")
    print_code("page_json = page_data.to_json()")
    
    try:
        page_dict = page_data.to_dict()
        page_json = page_data.to_json()
        
        print_success("Serialization successful!")
        print_info("Dictionary format:")
        print(json.dumps(page_dict, indent=2))
        print_info("\nJSON format:")
        print(page_json)
    except Exception as e:
        print_error(f"Serialization error: {e}")
    
    wait_for_enter()
    
    print("\n3. Creating update data:")
    print_code("""
update_data = PageUpdate(
    title="Updated Awesome Page",
    content="# Updated Content\\n\\nThis content has been updated!",
    tags=["awesome", "demo", "updated"]
)""")
    
    try:
        update_data = PageUpdate(
            title="Updated Awesome Page",
            content="# Updated Content\n\nThis content has been updated!",
            tags=["awesome", "demo", "updated"]
        )
        print_success("PageUpdate model created!")
        print_info(f"New title: {update_data.title}")
        print_info(f"New tags: {update_data.tags}")
    except Exception as e:
        print_error(f"Error creating update model: {e}")
    
    return page_data, update_data


@patch('wikijs.client.requests.Session')
def experiment_api_operations(mock_session_class, client, page_data, update_data):
    """Experiment with API operations."""
    print_header("🌐 API OPERATIONS EXPERIMENT")
    
    # Set up mock session
    mock_session = setup_mock_session()
    mock_session_class.return_value = mock_session
    
    print_info("Let's try different API operations with mocked responses!")
    
    print("\n1. Listing all pages:")
    print_code("pages = client.pages.list()")
    
    try:
        pages = client.pages.list()
        print_success(f"Found {len(pages)} pages!")
        for i, page in enumerate(pages[:3], 1):
            print_info(f"{i}. {page.title} ({page.path}) - {len(page.tags)} tags")
    except Exception as e:
        print_error(f"Error listing pages: {e}")
    
    wait_for_enter()
    
    print("\n2. Getting a specific page:")
    print_code("page = client.pages.get(1)")
    
    try:
        page = client.pages.get(1)
        print_success("Page retrieved!")
        print_info(f"Title: {page.title}")
        print_info(f"Path: {page.path}")
        print_info(f"Published: {page.is_published}")
        print_info(f"Content preview: {page.content[:50]}...")
    except Exception as e:
        print_error(f"Error getting page: {e}")
    
    wait_for_enter()
    
    print("\n3. Creating a new page:")
    print_code("new_page = client.pages.create(page_data)")
    
    try:
        new_page = client.pages.create(page_data)
        print_success("Page created!")
        print_info(f"New page ID: {new_page.id}")
        print_info(f"Title: {new_page.title}")
        print_info(f"Created at: {new_page.created_at}")
    except Exception as e:
        print_error(f"Error creating page: {e}")
    
    wait_for_enter()
    
    print("\n4. Updating a page:")
    print_code("updated_page = client.pages.update(1, update_data)")
    
    try:
        updated_page = client.pages.update(1, update_data)
        print_success("Page updated!")
        print_info(f"Updated title: {updated_page.title}")
        print_info(f"Updated at: {updated_page.updated_at}")
    except Exception as e:
        print_error(f"Error updating page: {e}")
    
    wait_for_enter()
    
    print("\n5. Searching pages:")
    print_code("search_results = client.pages.search('guide')")
    
    try:
        search_results = client.pages.search('guide')
        print_success(f"Found {len(search_results)} matching pages!")
        for result in search_results:
            print_info(f"• {result.title} - {result.path}")
    except Exception as e:
        print_error(f"Error searching pages: {e}")


def experiment_error_handling():
    """Experiment with error handling."""
    print_header("⚠️ ERROR HANDLING EXPERIMENT")
    
    print_info("Let's see how the SDK handles different types of errors!")
    
    print("\n1. Validation errors:")
    print_code("""
try:
    invalid_page = PageCreate(title="", path="", content="")
except ValidationError as e:
    print(f"Validation error: {e}")
""")
    
    try:
        invalid_page = PageCreate(title="", path="", content="")
        print_warning("Expected validation error, but none occurred!")
    except ValidationError as e:
        print_success(f"Caught validation error: {e}")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
    
    wait_for_enter()
    
    print("\n2. Authentication errors:")
    print_code("""
try:
    bad_auth = APIKeyAuth("")
except ValidationError as e:
    print(f"Auth error: {e}")
""")
    
    try:
        bad_auth = APIKeyAuth("")
        print_warning("Expected authentication error, but none occurred!")
    except ValidationError as e:
        print_success(f"Caught auth error: {e}")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
    
    wait_for_enter()
    
    print("\n3. URL validation errors:")
    print_code("""
try:
    from wikijs.utils.helpers import normalize_url
    normalize_url("")
except ValidationError as e:
    print(f"URL error: {e}")
""")
    
    try:
        from wikijs.utils.helpers import normalize_url
        normalize_url("")
        print_warning("Expected URL validation error!")
    except ValidationError as e:
        print_success(f"Caught URL error: {e}")
    except Exception as e:
        print_error(f"Unexpected error: {e}")


def experiment_utilities():
    """Experiment with utility functions."""
    print_header("🛠️ UTILITIES EXPERIMENT")
    
    print_info("Let's try out the SDK's utility functions!")
    
    from wikijs.utils.helpers import (
        normalize_url, sanitize_path, chunk_list, 
        safe_get, build_api_url
    )
    
    print("\n1. URL normalization:")
    test_urls = [
        "wiki.example.com",
        "https://wiki.example.com/",
        "localhost:3000",
        "wiki.company.internal:8080/"
    ]
    
    for url in test_urls:
        try:
            normalized = normalize_url(url)
            print_success(f"'{url}' → '{normalized}'")
        except Exception as e:
            print_error(f"'{url}' → Error: {e}")
    
    wait_for_enter()
    
    print("\n2. Path sanitization:")
    test_paths = [
        "hello world",
        "/my/wiki/page/",
        "special-chars!@#$",
        "  multiple   spaces  "
    ]
    
    for path in test_paths:
        try:
            sanitized = sanitize_path(path)
            print_success(f"'{path}' → '{sanitized}'")
        except Exception as e:
            print_error(f"'{path}' → Error: {e}")
    
    wait_for_enter()
    
    print("\n3. List chunking:")
    test_list = list(range(1, 13))  # [1, 2, 3, ..., 12]
    chunk_sizes = [3, 4, 5]
    
    for size in chunk_sizes:
        chunks = chunk_list(test_list, size)
        print_success(f"Chunks of {size}: {chunks}")
    
    wait_for_enter()
    
    print("\n4. Safe dictionary access:")
    test_data = {
        "user": {
            "profile": {
                "name": "John Doe",
                "email": "john@example.com"
            }
        },
        "settings": {
            "theme": "dark",
            "notifications": True
        }
    }
    
    test_keys = [
        "user.profile.name",
        "user.profile.email", 
        "settings.theme",
        "user.missing.key",
        "nonexistent"
    ]
    
    for key in test_keys:
        value = safe_get(test_data, key, "NOT_FOUND")
        print_success(f"'{key}' → {value}")


def main():
    """Main experimentation function."""
    print_header("🧪 WIKI.JS SDK EXPERIMENTATION LAB")
    
    print(f"{Colors.CYAN}Welcome to the Wiki.js Python SDK Experiment Lab!{Colors.END}")
    print(f"{Colors.CYAN}Here you can safely try out all the SDK features with mocked data.{Colors.END}")
    
    wait_for_enter("Ready to start experimenting?")
    
    # Experiment with different features
    client = experiment_client_setup()
    page_data, update_data = experiment_data_models()
    experiment_api_operations(client, page_data, update_data)
    experiment_error_handling()
    experiment_utilities()
    
    # Final summary
    print_header("🎉 EXPERIMENT COMPLETE")
    print_success("Congratulations! You've experimented with:")
    print_info("✨ Client setup and authentication")
    print_info("✨ Data models and serialization")
    print_info("✨ API operations (mocked)")
    print_info("✨ Error handling")
    print_info("✨ Utility functions")
    
    print(f"\n{Colors.YELLOW}💡 Next steps:{Colors.END}")
    print(f"{Colors.CYAN}1. Check out the examples/ directory for real-world usage{Colors.END}")
    print(f"{Colors.CYAN}2. Read the docs/user_guide.md for detailed documentation{Colors.END}")
    print(f"{Colors.CYAN}3. Try connecting to a real Wiki.js instance{Colors.END}")
    
    print(f"\n{Colors.GREEN}Happy coding with Wiki.js SDK! 🚀{Colors.END}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Experiment interrupted. Goodbye! 👋{Colors.END}")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)