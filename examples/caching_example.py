#!/usr/bin/env python3
"""Example: Using intelligent caching for improved performance.

This example demonstrates how to use the caching system to reduce API calls
and improve application performance.
"""

import time

from wikijs import WikiJSClient
from wikijs.cache import MemoryCache


def main():
    """Demonstrate caching functionality."""
    # Create cache with 5-minute TTL and max 1000 items
    cache = MemoryCache(ttl=300, max_size=1000)

    # Enable caching on client
    client = WikiJSClient(
        "https://wiki.example.com",
        auth="your-api-key-here",
        cache=cache
    )

    print("=" * 60)
    print("Wiki.js SDK - Caching Example")
    print("=" * 60)
    print()

    # Example 1: Basic caching demonstration
    print("1. Basic Caching")
    print("-" * 60)

    page_id = 123

    # First call - hits the API
    print(f"Fetching page {page_id} (first time)...")
    start = time.time()
    page = client.pages.get(page_id)
    first_call_time = time.time() - start
    print(f"  Time: {first_call_time*1000:.2f}ms")
    print(f"  Title: {page.title}")
    print()

    # Second call - returns from cache
    print(f"Fetching page {page_id} (second time)...")
    start = time.time()
    page = client.pages.get(page_id)
    second_call_time = time.time() - start
    print(f"  Time: {second_call_time*1000:.2f}ms")
    print(f"  Title: {page.title}")
    print(f"  Speed improvement: {first_call_time/second_call_time:.1f}x faster!")
    print()

    # Example 2: Cache statistics
    print("2. Cache Statistics")
    print("-" * 60)
    stats = cache.get_stats()
    print(f"  Cache hit rate: {stats['hit_rate']}")
    print(f"  Total requests: {stats['total_requests']}")
    print(f"  Cache hits: {stats['hits']}")
    print(f"  Cache misses: {stats['misses']}")
    print(f"  Current size: {stats['current_size']}/{stats['max_size']}")
    print()

    # Example 3: Cache invalidation on updates
    print("3. Automatic Cache Invalidation")
    print("-" * 60)
    print("Updating page (cache will be automatically invalidated)...")
    client.pages.update(page_id, {"content": "Updated content"})
    print("  Cache invalidated for this page")
    print()

    print("Next get() will fetch fresh data from API...")
    start = time.time()
    page = client.pages.get(page_id)
    time_after_update = time.time() - start
    print(f"  Time: {time_after_update*1000:.2f}ms (fresh from API)")
    print()

    # Example 4: Manual cache invalidation
    print("4. Manual Cache Invalidation")
    print("-" * 60)

    # Get some pages to cache them
    print("Caching multiple pages...")
    for i in range(1, 6):
        try:
            client.pages.get(i)
            print(f"  Cached page {i}")
        except Exception:
            pass

    stats = cache.get_stats()
    print(f"Cache size: {stats['current_size']} items")
    print()

    # Invalidate specific page
    print("Invalidating page 123...")
    cache.invalidate_resource('page', '123')
    print("  Specific page invalidated")
    print()

    # Invalidate all pages
    print("Invalidating all pages...")
    cache.invalidate_resource('page')
    print("  All pages invalidated")
    print()

    # Clear entire cache
    print("Clearing entire cache...")
    cache.clear()
    stats = cache.get_stats()
    print(f"  Cache cleared: {stats['current_size']} items remaining")
    print()

    # Example 5: Cache with multiple clients
    print("5. Shared Cache Across Clients")
    print("-" * 60)

    # Same cache can be shared across multiple clients
    client2 = WikiJSClient(
        "https://wiki.example.com",
        auth="your-api-key-here",
        cache=cache  # Share the same cache
    )

    print("Client 1 fetches page...")
    page = client.pages.get(page_id)
    print(f"  Cached by client 1")
    print()

    print("Client 2 fetches same page (from shared cache)...")
    start = time.time()
    page = client2.pages.get(page_id)
    shared_time = time.time() - start
    print(f"  Time: {shared_time*1000:.2f}ms")
    print(f"  Retrieved from shared cache!")
    print()

    # Example 6: Cache cleanup
    print("6. Cache Cleanup")
    print("-" * 60)

    # Create cache with short TTL for demo
    short_cache = MemoryCache(ttl=1)  # 1 second TTL
    short_client = WikiJSClient(
        "https://wiki.example.com",
        auth="your-api-key-here",
        cache=short_cache
    )

    # Cache some pages
    print("Caching pages with 1-second TTL...")
    for i in range(1, 4):
        try:
            short_client.pages.get(i)
        except Exception:
            pass

    stats = short_cache.get_stats()
    print(f"  Cached: {stats['current_size']} items")
    print()

    print("Waiting for cache to expire...")
    time.sleep(1.1)

    # Manual cleanup
    removed = short_cache.cleanup_expired()
    print(f"  Cleaned up: {removed} expired items")

    stats = short_cache.get_stats()
    print(f"  Remaining: {stats['current_size']} items")
    print()

    print("=" * 60)
    print("Caching example complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
