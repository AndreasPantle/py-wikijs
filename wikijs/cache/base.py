"""Base cache interface for wikijs-python-sdk."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class CacheKey:
    """Cache key structure for Wiki.js resources.

    Attributes:
        resource_type: Type of resource (e.g., 'page', 'user', 'group')
        identifier: Unique identifier (ID, path, etc.)
        operation: Operation type (e.g., 'get', 'list')
        params: Additional parameters as string (e.g., 'locale=en&tags=api')
    """

    resource_type: str
    identifier: str
    operation: str = "get"
    params: Optional[str] = None

    def to_string(self) -> str:
        """Convert cache key to string format.

        Returns:
            String representation suitable for cache storage

        Example:
            >>> key = CacheKey('page', '123', 'get')
            >>> key.to_string()
            'page:123:get'
        """
        parts = [self.resource_type, str(self.identifier), self.operation]
        if self.params:
            parts.append(self.params)
        return ":".join(parts)


class BaseCache(ABC):
    """Abstract base class for cache implementations.

    All cache backends must implement this interface to be compatible
    with the WikiJS SDK.

    Args:
        ttl: Time-to-live in seconds (default: 300 = 5 minutes)
        max_size: Maximum number of items to cache (default: 1000)
    """

    def __init__(self, ttl: int = 300, max_size: int = 1000):
        """Initialize cache with TTL and size limits.

        Args:
            ttl: Time-to-live in seconds for cached items
            max_size: Maximum number of items to store
        """
        self.ttl = ttl
        self.max_size = max_size

    @abstractmethod
    def get(self, key: CacheKey) -> Optional[Any]:
        """Retrieve value from cache.

        Args:
            key: Cache key to retrieve

        Returns:
            Cached value if found and not expired, None otherwise
        """
        pass

    @abstractmethod
    def set(self, key: CacheKey, value: Any) -> None:
        """Store value in cache.

        Args:
            key: Cache key to store under
            value: Value to cache
        """
        pass

    @abstractmethod
    def delete(self, key: CacheKey) -> None:
        """Remove value from cache.

        Args:
            key: Cache key to remove
        """
        pass

    @abstractmethod
    def clear(self) -> None:
        """Clear all cached values."""
        pass

    @abstractmethod
    def invalidate_resource(self, resource_type: str, identifier: Optional[str] = None) -> None:
        """Invalidate all cache entries for a resource.

        Args:
            resource_type: Type of resource to invalidate (e.g., 'page', 'user')
            identifier: Specific identifier to invalidate (None = all of that type)

        Example:
            >>> cache.invalidate_resource('page', '123')  # Invalidate page 123
            >>> cache.invalidate_resource('page')  # Invalidate all pages
        """
        pass

    def get_stats(self) -> dict:
        """Get cache statistics.

        Returns:
            Dictionary with cache statistics (hits, misses, size, etc.)
        """
        return {
            "ttl": self.ttl,
            "max_size": self.max_size,
        }
