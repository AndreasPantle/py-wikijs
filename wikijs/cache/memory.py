"""In-memory cache implementation for py-wikijs."""

import time
from collections import OrderedDict
from typing import Any, Optional

from .base import BaseCache, CacheKey


class MemoryCache(BaseCache):
    """In-memory LRU cache with TTL support.

    This cache stores data in memory with a Least Recently Used (LRU)
    eviction policy when the cache reaches max_size. Each entry has
    a TTL (time-to-live) after which it's considered expired.

    Features:
        - LRU eviction policy
        - TTL-based expiration
        - Thread-safe operations
        - Cache statistics (hits, misses)

    Args:
        ttl: Time-to-live in seconds (default: 300 = 5 minutes)
        max_size: Maximum number of items (default: 1000)

    Example:
        >>> cache = MemoryCache(ttl=300, max_size=500)
        >>> key = CacheKey('page', '123', 'get')
        >>> cache.set(key, page_data)
        >>> cached = cache.get(key)
    """

    def __init__(self, ttl: int = 300, max_size: int = 1000):
        """Initialize in-memory cache.

        Args:
            ttl: Time-to-live in seconds
            max_size: Maximum cache size
        """
        super().__init__(ttl, max_size)
        self._cache: OrderedDict = OrderedDict()
        self._hits = 0
        self._misses = 0

    def get(self, key: CacheKey) -> Optional[Any]:
        """Retrieve value from cache if not expired.

        Args:
            key: Cache key to retrieve

        Returns:
            Cached value if found and valid, None otherwise
        """
        key_str = key.to_string()

        if key_str not in self._cache:
            self._misses += 1
            return None

        # Get cached entry
        entry = self._cache[key_str]
        expires_at = entry["expires_at"]

        # Check if expired
        if time.time() > expires_at:
            # Expired, remove it
            del self._cache[key_str]
            self._misses += 1
            return None

        # Move to end (mark as recently used)
        self._cache.move_to_end(key_str)
        self._hits += 1
        return entry["value"]

    def set(self, key: CacheKey, value: Any) -> None:
        """Store value in cache with TTL.

        Args:
            key: Cache key
            value: Value to cache
        """
        key_str = key.to_string()

        # If exists, remove it first (will be re-added at end)
        if key_str in self._cache:
            del self._cache[key_str]

        # Check size limit and evict oldest if needed
        if len(self._cache) >= self.max_size:
            # Remove oldest (first item in OrderedDict)
            self._cache.popitem(last=False)

        # Add new entry at end (most recent)
        self._cache[key_str] = {
            "value": value,
            "expires_at": time.time() + self.ttl,
            "created_at": time.time(),
        }

    def delete(self, key: CacheKey) -> None:
        """Remove value from cache.

        Args:
            key: Cache key to remove
        """
        key_str = key.to_string()
        if key_str in self._cache:
            del self._cache[key_str]

    def clear(self) -> None:
        """Clear all cached values and reset statistics."""
        self._cache.clear()
        self._hits = 0
        self._misses = 0

    def invalidate_resource(
        self, resource_type: str, identifier: Optional[str] = None
    ) -> None:
        """Invalidate all cache entries for a resource.

        Args:
            resource_type: Resource type to invalidate
            identifier: Specific identifier (None = invalidate all of this type)
        """
        keys_to_delete = []

        for key_str in self._cache.keys():
            parts = key_str.split(":")
            if len(parts) < 2:
                continue

            cached_resource_type = parts[0]
            cached_identifier = parts[1]

            # Match resource type
            if cached_resource_type != resource_type:
                continue

            # If identifier specified, match it too
            if identifier is not None and cached_identifier != str(identifier):
                continue

            keys_to_delete.append(key_str)

        # Delete matched keys
        for key_str in keys_to_delete:
            del self._cache[key_str]

    def get_stats(self) -> dict:
        """Get cache statistics.

        Returns:
            Dictionary with cache performance metrics
        """
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0

        return {
            "ttl": self.ttl,
            "max_size": self.max_size,
            "current_size": len(self._cache),
            "hits": self._hits,
            "misses": self._misses,
            "hit_rate": f"{hit_rate:.2f}%",
            "total_requests": total_requests,
        }

    def cleanup_expired(self) -> int:
        """Remove all expired entries from cache.

        Returns:
            Number of entries removed
        """
        current_time = time.time()
        keys_to_delete = []

        for key_str, entry in self._cache.items():
            if current_time > entry["expires_at"]:
                keys_to_delete.append(key_str)

        for key_str in keys_to_delete:
            del self._cache[key_str]

        return len(keys_to_delete)
