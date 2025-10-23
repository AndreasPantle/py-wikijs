"""Tests for Pages endpoint caching functionality."""
import pytest
from unittest.mock import MagicMock, Mock

from wikijs.cache import MemoryCache, CacheKey
from wikijs.endpoints.pages import PagesEndpoint
from wikijs.models import Page


class TestPagesCaching:
    """Test caching behavior in Pages endpoint."""

    def test_get_with_cache_hit(self):
        """Test page retrieval uses cache when available."""
        # Setup
        cache = MemoryCache(ttl=300)
        client = MagicMock()
        client.cache = cache
        client._request = MagicMock()

        pages = PagesEndpoint(client)

        # Pre-populate cache
        page_data = {"id": 123, "title": "Test", "path": "test"}
        cache_key = CacheKey("page", "123", "get")
        cache.set(cache_key, page_data)

        # Execute
        result = pages.get(123)

        # Verify cache was used, not API
        client._request.assert_not_called()
        assert result["id"] == 123

    def test_get_with_cache_miss(self):
        """Test page retrieval calls API on cache miss."""
        # Setup
        cache = MemoryCache(ttl=300)
        client = MagicMock()
        client.cache = cache

        # Mock the _post method on the endpoint
        pages = PagesEndpoint(client)
        pages._post = Mock(return_value={
            "data": {"pages": {"single": {
                "id": 123,
                "title": "Test",
                "path": "test",
                "content": "Test content",
                "description": "Test desc",
                "isPublished": True,
                "isPrivate": False,
                "tags": [],
                "locale": "en",
                "authorId": 1,
                "authorName": "Test User",
                "authorEmail": "test@example.com",
                "editor": "markdown",
                "createdAt": "2023-01-01T00:00:00Z",
                "updatedAt": "2023-01-02T00:00:00Z"
            }}}
        })

        # Execute
        result = pages.get(123)

        # Verify API was called
        pages._post.assert_called_once()

        # Verify result was cached
        cache_key = CacheKey("page", "123", "get")
        cached = cache.get(cache_key)
        assert cached is not None

    def test_update_invalidates_cache(self):
        """Test page update invalidates cache."""
        # Setup
        cache = MemoryCache(ttl=300)
        client = MagicMock()
        client.cache = cache

        pages = PagesEndpoint(client)
        pages._post = Mock(return_value={
            "data": {"updatePage": {
                "id": 123,
                "title": "New",
                "path": "test",
                "content": "Updated content",
                "description": "Updated desc",
                "isPublished": True,
                "isPrivate": False,
                "tags": [],
                "locale": "en",
                "authorId": 1,
                "authorName": "Test User",
                "authorEmail": "test@example.com",
                "editor": "markdown",
                "createdAt": "2023-01-01T00:00:00Z",
                "updatedAt": "2023-01-02T00:00:00Z"
            }}
        })

        # Pre-populate cache
        cache_key = CacheKey("page", "123", "get")
        cache.set(cache_key, {"id": 123, "title": "Old"})

        # Verify cache is populated
        assert cache.get(cache_key) is not None

        # Execute update
        pages.update(123, {"title": "New"})

        # Verify cache was invalidated
        cached = cache.get(cache_key)
        assert cached is None

    def test_delete_invalidates_cache(self):
        """Test page delete invalidates cache."""
        # Setup
        cache = MemoryCache(ttl=300)
        client = MagicMock()
        client.cache = cache

        pages = PagesEndpoint(client)
        pages._post = Mock(return_value={
            "data": {"deletePage": {"success": True}}
        })

        # Pre-populate cache
        cache_key = CacheKey("page", "123", "get")
        cache.set(cache_key, {"id": 123, "title": "Test"})

        # Verify cache is populated
        assert cache.get(cache_key) is not None

        # Execute delete
        pages.delete(123)

        # Verify cache was invalidated
        cached = cache.get(cache_key)
        assert cached is None

    def test_get_without_cache(self):
        """Test page retrieval without cache configured."""
        # Setup
        client = MagicMock()
        client.cache = None

        pages = PagesEndpoint(client)
        pages._post = Mock(return_value={
            "data": {"pages": {"single": {
                "id": 123,
                "title": "Test",
                "path": "test",
                "content": "Test content",
                "description": "Test desc",
                "isPublished": True,
                "isPrivate": False,
                "tags": [],
                "locale": "en",
                "authorId": 1,
                "authorName": "Test User",
                "authorEmail": "test@example.com",
                "editor": "markdown",
                "createdAt": "2023-01-01T00:00:00Z",
                "updatedAt": "2023-01-02T00:00:00Z"
            }}}
        })

        # Execute
        result = pages.get(123)

        # Verify API was called
        pages._post.assert_called_once()
        assert result.id == 123
