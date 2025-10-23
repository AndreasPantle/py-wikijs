"""Basic async usage examples for Wiki.js Python SDK.

This example demonstrates how to use the AsyncWikiJSClient for
high-performance concurrent operations with Wiki.js.

Requirements:
    pip install py-wikijs[async]
"""

import asyncio
from typing import List

from wikijs.aio import AsyncWikiJSClient
from wikijs.models.page import Page, PageCreate, PageUpdate


async def basic_operations_example():
    """Demonstrate basic async CRUD operations."""
    print("\n=== Basic Async Operations ===\n")

    # Create client with async context manager (automatic cleanup)
    async with AsyncWikiJSClient(
        base_url="https://wiki.example.com", auth="your-api-key-here"
    ) as client:
        # Test connection
        try:
            connected = await client.test_connection()
            print(f"✓ Connected to Wiki.js: {connected}")
        except Exception as e:
            print(f"✗ Connection failed: {e}")
            return

        # List all pages
        print("\nListing pages...")
        pages = await client.pages.list(limit=5)
        print(f"Found {len(pages)} pages:")
        for page in pages:
            print(f"  - {page.title} ({page.path})")

        # Get a specific page by ID
        if pages:
            page_id = pages[0].id
            print(f"\nGetting page {page_id}...")
            page = await client.pages.get(page_id)
            print(f"  Title: {page.title}")
            print(f"  Path: {page.path}")
            print(f"  Content length: {len(page.content)} chars")

        # Search for pages
        print("\nSearching for 'documentation'...")
        results = await client.pages.search("documentation", limit=3)
        print(f"Found {len(results)} matching pages")


async def concurrent_operations_example():
    """Demonstrate concurrent async operations for better performance."""
    print("\n=== Concurrent Operations (High Performance) ===\n")

    async with AsyncWikiJSClient(
        base_url="https://wiki.example.com", auth="your-api-key-here"
    ) as client:
        # Fetch multiple pages concurrently
        page_ids = [1, 2, 3, 4, 5]

        print(f"Fetching {len(page_ids)} pages concurrently...")

        # Sequential approach (slow)
        import time

        start = time.time()
        sequential_pages: List[Page] = []
        for page_id in page_ids:
            try:
                page = await client.pages.get(page_id)
                sequential_pages.append(page)
            except Exception:
                pass
        sequential_time = time.time() - start

        # Concurrent approach (fast!)
        start = time.time()
        tasks = [client.pages.get(page_id) for page_id in page_ids]
        concurrent_pages = await asyncio.gather(*tasks, return_exceptions=True)
        # Filter out exceptions
        concurrent_pages = [p for p in concurrent_pages if isinstance(p, Page)]
        concurrent_time = time.time() - start

        print(f"\nSequential: {sequential_time:.2f}s")
        print(f"Concurrent: {concurrent_time:.2f}s")
        print(f"Speedup: {sequential_time / concurrent_time:.1f}x faster")


async def crud_operations_example():
    """Demonstrate Create, Read, Update, Delete operations."""
    print("\n=== CRUD Operations ===\n")

    async with AsyncWikiJSClient(
        base_url="https://wiki.example.com", auth="your-api-key-here"
    ) as client:
        # Create a new page
        print("Creating new page...")
        new_page_data = PageCreate(
            title="Async SDK Example",
            path="async-sdk-example",
            content="# Async SDK Example\n\nCreated with async client!",
            description="Example page created with async operations",
            tags=["example", "async", "sdk"],
        )

        try:
            created_page = await client.pages.create(new_page_data)
            print(f"✓ Created page: {created_page.title} (ID: {created_page.id})")

            # Update the page
            print("\nUpdating page...")
            update_data = PageUpdate(
                title="Async SDK Example (Updated)",
                content="# Async SDK Example\n\nUpdated content!",
                tags=["example", "async", "sdk", "updated"],
            )

            updated_page = await client.pages.update(created_page.id, update_data)
            print(f"✓ Updated page: {updated_page.title}")

            # Read the updated page
            print("\nReading updated page...")
            fetched_page = await client.pages.get(created_page.id)
            print(f"✓ Fetched page: {fetched_page.title}")
            print(f"  Tags: {', '.join(fetched_page.tags)}")

            # Delete the page
            print("\nDeleting page...")
            deleted = await client.pages.delete(created_page.id)
            print(f"✓ Deleted: {deleted}")

        except Exception as e:
            print(f"✗ Error: {e}")


async def error_handling_example():
    """Demonstrate proper error handling with async operations."""
    print("\n=== Error Handling ===\n")

    async with AsyncWikiJSClient(
        base_url="https://wiki.example.com", auth="invalid-key"
    ) as client:
        # Handle authentication errors
        try:
            await client.test_connection()
            print("✓ Connection successful")
        except Exception as e:
            print(f"✗ Expected authentication error: {type(e).__name__}")

    # Handle not found errors
    async with AsyncWikiJSClient(
        base_url="https://wiki.example.com", auth="your-api-key-here"
    ) as client:
        try:
            page = await client.pages.get(999999)
            print(f"Found page: {page.title}")
        except Exception as e:
            print(f"✗ Expected not found error: {type(e).__name__}")


async def advanced_filtering_example():
    """Demonstrate advanced filtering and searching."""
    print("\n=== Advanced Filtering ===\n")

    async with AsyncWikiJSClient(
        base_url="https://wiki.example.com", auth="your-api-key-here"
    ) as client:
        # Filter by tags
        print("Finding pages with specific tags...")
        tagged_pages = await client.pages.get_by_tags(
            tags=["documentation", "api"], match_all=True  # Must have ALL tags
        )
        print(f"Found {len(tagged_pages)} pages with both tags")

        # Search with locale
        print("\nSearching in specific locale...")
        results = await client.pages.search("guide", locale="en")
        print(f"Found {len(results)} English pages")

        # List with ordering
        print("\nListing recent pages...")
        recent_pages = await client.pages.list(
            limit=5, order_by="updated_at", order_direction="DESC"
        )
        print("Most recently updated:")
        for page in recent_pages:
            print(f"  - {page.title}")


async def main():
    """Run all examples."""
    print("=" * 60)
    print("Wiki.js Python SDK - Async Usage Examples")
    print("=" * 60)

    # Run examples
    await basic_operations_example()

    # Uncomment to run other examples:
    # await concurrent_operations_example()
    # await crud_operations_example()
    # await error_handling_example()
    # await advanced_filtering_example()

    print("\n" + "=" * 60)
    print("Examples complete!")
    print("=" * 60)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
