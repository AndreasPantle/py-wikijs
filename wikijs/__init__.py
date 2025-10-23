"""Wiki.js Python SDK - Professional SDK for Wiki.js API integration.

This package provides a comprehensive Python SDK for interacting with Wiki.js
instances, including support for pages, users, groups, and system management.

Example:
    Synchronous usage:

    >>> from wikijs import WikiJSClient
    >>> client = WikiJSClient('https://wiki.example.com', auth='your-api-key')
    >>> pages = client.pages.list()

    Asynchronous usage (requires aiohttp):

    >>> from wikijs.aio import AsyncWikiJSClient
    >>> async with AsyncWikiJSClient('https://wiki.example.com', auth='key') as client:
    ...     pages = await client.pages.list()

Features:
    - Synchronous and asynchronous clients
    - Type-safe data models with validation
    - Comprehensive error handling
    - Automatic retry logic with exponential backoff
    - Professional logging and debugging support
    - Context manager support for resource cleanup
    - High-performance async operations with connection pooling
"""

from .auth import APIKeyAuth, AuthHandler, JWTAuth, NoAuth
from .client import WikiJSClient
from .exceptions import (
    APIError,
    AuthenticationError,
    ClientError,
    ConfigurationError,
    ConnectionError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ValidationError,
    WikiJSException,
)
from .models import BaseModel, Page, PageCreate, PageUpdate
from .version import __version__, __version_info__

# Public API
__all__ = [
    # Main client
    "WikiJSClient",
    # Authentication
    "AuthHandler",
    "NoAuth",
    "APIKeyAuth",
    "JWTAuth",
    # Data models
    "BaseModel",
    "Page",
    "PageCreate",
    "PageUpdate",
    # Exceptions
    "WikiJSException",
    "APIError",
    "AuthenticationError",
    "ConfigurationError",
    "ValidationError",
    "ClientError",
    "ServerError",
    "NotFoundError",
    "PermissionError",
    "RateLimitError",
    "ConnectionError",
    "TimeoutError",
    # Version info
    "__version__",
    "__version_info__",
]

# Package metadata
__author__ = "Wiki.js SDK Contributors"
__email__ = ""
__license__ = "MIT"
__description__ = "Professional Python SDK for Wiki.js API integration"
__url__ = "https://github.com/yourusername/py-wikijs"

# For type checking
__all__ += [
    "__author__",
    "__email__",
    "__license__",
    "__description__",
    "__url__",
]
