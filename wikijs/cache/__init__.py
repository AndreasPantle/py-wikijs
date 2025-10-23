"""Caching module for py-wikijs.

This module provides intelligent caching for frequently accessed Wiki.js resources
like pages, users, and groups. It supports multiple cache backends and TTL-based
expiration.

Example:
    >>> from wikijs import WikiJSClient
    >>> from wikijs.cache import MemoryCache
    >>>
    >>> cache = MemoryCache(ttl=300)  # 5 minute TTL
    >>> client = WikiJSClient('https://wiki.example.com', auth='api-key', cache=cache)
    >>>
    >>> # First call hits the API
    >>> page = client.pages.get(123)
    >>>
    >>> # Second call returns cached result
    >>> page = client.pages.get(123)  # Instant response
"""

from .base import BaseCache, CacheKey
from .memory import MemoryCache

__all__ = ["BaseCache", "CacheKey", "MemoryCache"]
