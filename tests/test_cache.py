"""Tests for caching module."""

import time
from unittest.mock import Mock

import pytest

from wikijs.cache import CacheKey, MemoryCache
from wikijs.models import Page


class TestCacheKey:
    """Tests for CacheKey class."""

    def test_cache_key_to_string_basic(self):
        """Test basic cache key string generation."""
        key = CacheKey("page", "123", "get")
        assert key.to_string() == "page:123:get"

    def test_cache_key_to_string_with_params(self):
        """Test cache key string with parameters."""
        key = CacheKey("page", "123", "list", "locale=en&tags=api")
        assert key.to_string() == "page:123:list:locale=en&tags=api"

    def test_cache_key_different_resource_types(self):
        """Test cache keys for different resource types."""
        page_key = CacheKey("page", "1", "get")
        user_key = CacheKey("user", "1", "get")
        assert page_key.to_string() != user_key.to_string()


class TestMemoryCache:
    """Tests for MemoryCache class."""

    def test_init_default_values(self):
        """Test cache initialization with default values."""
        cache = MemoryCache()
        assert cache.ttl == 300
        assert cache.max_size == 1000

    def test_init_custom_values(self):
        """Test cache initialization with custom values."""
        cache = MemoryCache(ttl=600, max_size=500)
        assert cache.ttl == 600
        assert cache.max_size == 500

    def test_set_and_get(self):
        """Test setting and getting cache values."""
        cache = MemoryCache(ttl=10)
        key = CacheKey("page", "123", "get")
        value = {"id": 123, "title": "Test Page"}

        cache.set(key, value)
        cached = cache.get(key)

        assert cached == value

    def test_get_nonexistent_key(self):
        """Test getting a key that doesn't exist."""
        cache = MemoryCache()
        key = CacheKey("page", "999", "get")
        assert cache.get(key) is None

    def test_ttl_expiration(self):
        """Test that cache entries expire after TTL."""
        cache = MemoryCache(ttl=1)  # 1 second TTL
        key = CacheKey("page", "123", "get")
        value = {"id": 123, "title": "Test Page"}

        cache.set(key, value)
        assert cache.get(key) == value

        # Wait for expiration
        time.sleep(1.1)
        assert cache.get(key) is None

    def test_lru_eviction(self):
        """Test LRU eviction when max_size is reached."""
        cache = MemoryCache(ttl=300, max_size=3)

        # Add 3 items
        for i in range(1, 4):
            key = CacheKey("page", str(i), "get")
            cache.set(key, {"id": i})

        # All 3 should be present
        assert cache.get(CacheKey("page", "1", "get")) is not None
        assert cache.get(CacheKey("page", "2", "get")) is not None
        assert cache.get(CacheKey("page", "3", "get")) is not None

        # Add 4th item - should evict oldest (1)
        cache.set(CacheKey("page", "4", "get"), {"id": 4})

        # Item 1 should be evicted
        assert cache.get(CacheKey("page", "1", "get")) is None
        # Others should still be present
        assert cache.get(CacheKey("page", "2", "get")) is not None
        assert cache.get(CacheKey("page", "3", "get")) is not None
        assert cache.get(CacheKey("page", "4", "get")) is not None

    def test_lru_access_updates_order(self):
        """Test that accessing an item updates LRU order."""
        cache = MemoryCache(ttl=300, max_size=3)

        # Add 3 items
        for i in range(1, 4):
            cache.set(CacheKey("page", str(i), "get"), {"id": i})

        # Access item 1 (makes it most recent)
        cache.get(CacheKey("page", "1", "get"))

        # Add 4th item - should evict item 2 (oldest now)
        cache.set(CacheKey("page", "4", "get"), {"id": 4})

        # Item 1 should still be present (was accessed)
        assert cache.get(CacheKey("page", "1", "get")) is not None
        # Item 2 should be evicted
        assert cache.get(CacheKey("page", "2", "get")) is None

    def test_delete(self):
        """Test deleting cache entries."""
        cache = MemoryCache()
        key = CacheKey("page", "123", "get")
        cache.set(key, {"id": 123})

        assert cache.get(key) is not None
        cache.delete(key)
        assert cache.get(key) is None

    def test_clear(self):
        """Test clearing all cache entries."""
        cache = MemoryCache()

        # Add multiple items
        for i in range(5):
            cache.set(CacheKey("page", str(i), "get"), {"id": i})

        # Clear cache
        cache.clear()

        # All items should be gone
        for i in range(5):
            assert cache.get(CacheKey("page", str(i), "get")) is None

    def test_invalidate_resource_specific(self):
        """Test invalidating a specific resource."""
        cache = MemoryCache()

        # Add multiple pages
        for i in range(1, 4):
            cache.set(CacheKey("page", str(i), "get"), {"id": i})

        # Invalidate page 2
        cache.invalidate_resource("page", "2")

        # Page 2 should be gone
        assert cache.get(CacheKey("page", "2", "get")) is None
        # Others should remain
        assert cache.get(CacheKey("page", "1", "get")) is not None
        assert cache.get(CacheKey("page", "3", "get")) is not None

    def test_invalidate_resource_all(self):
        """Test invalidating all resources of a type."""
        cache = MemoryCache()

        # Add multiple pages and a user
        for i in range(1, 4):
            cache.set(CacheKey("page", str(i), "get"), {"id": i})
        cache.set(CacheKey("user", "1", "get"), {"id": 1})

        # Invalidate all pages
        cache.invalidate_resource("page")

        # All pages should be gone
        for i in range(1, 4):
            assert cache.get(CacheKey("page", str(i), "get")) is None

        # User should remain
        assert cache.get(CacheKey("user", "1", "get")) is not None

    def test_get_stats(self):
        """Test getting cache statistics."""
        cache = MemoryCache(ttl=300, max_size=1000)

        # Initially empty
        stats = cache.get_stats()
        assert stats["ttl"] == 300
        assert stats["max_size"] == 1000
        assert stats["current_size"] == 0
        assert stats["hits"] == 0
        assert stats["misses"] == 0

        # Add item and access it
        key = CacheKey("page", "123", "get")
        cache.set(key, {"id": 123})
        cache.get(key)  # Hit
        cache.get(CacheKey("page", "999", "get"))  # Miss

        stats = cache.get_stats()
        assert stats["current_size"] == 1
        assert stats["hits"] == 1
        assert stats["misses"] == 1
        assert "hit_rate" in stats

    def test_cleanup_expired(self):
        """Test cleanup of expired entries."""
        cache = MemoryCache(ttl=1)

        # Add items
        for i in range(3):
            cache.set(CacheKey("page", str(i), "get"), {"id": i})

        assert cache.get_stats()["current_size"] == 3

        # Wait for expiration
        time.sleep(1.1)

        # Run cleanup
        removed = cache.cleanup_expired()

        assert removed == 3
        assert cache.get_stats()["current_size"] == 0

    def test_set_updates_existing(self):
        """Test that setting an existing key updates the value."""
        cache = MemoryCache()
        key = CacheKey("page", "123", "get")

        cache.set(key, {"id": 123, "title": "Original"})
        assert cache.get(key)["title"] == "Original"

        cache.set(key, {"id": 123, "title": "Updated"})
        assert cache.get(key)["title"] == "Updated"
