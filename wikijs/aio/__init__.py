"""Async support for Wiki.js Python SDK.

This module provides asynchronous versions of the Wiki.js client and endpoints
using aiohttp for improved performance with concurrent requests.

Example:
    Basic async usage:

    >>> from wikijs.aio import AsyncWikiJSClient
    >>> async with AsyncWikiJSClient('https://wiki.example.com', auth='key') as client:
    ...     page = await client.pages.get(123)
    ...     pages = await client.pages.list()

Features:
    - Async/await support with aiohttp
    - Connection pooling and resource management
    - Context manager support for automatic cleanup
    - Same interface as sync client
    - Significantly improved performance for concurrent requests

Performance:
    The async client can achieve >3x throughput compared to the sync client
    when making multiple concurrent requests (100+ requests).
"""

from .client import AsyncWikiJSClient

__all__ = [
    "AsyncWikiJSClient",
]
