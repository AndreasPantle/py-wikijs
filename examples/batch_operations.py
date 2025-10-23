#!/usr/bin/env python3
"""Example: Using batch operations for bulk page management.

This example demonstrates how to use batch operations to efficiently
create, update, and delete multiple pages.
"""

import time

from wikijs import WikiJSClient
from wikijs.exceptions import APIError
from wikijs.models import PageCreate


def main():
    """Demonstrate batch operations."""
    client = WikiJSClient(
        "https://wiki.example.com",
        auth="your-api-key-here"
    )

    print("=" * 60)
    print("Wiki.js SDK - Batch Operations Example")
    print("=" * 60)
    print()

    # Example 1: Batch create pages
    print("1. Batch Create Pages")
    print("-" * 60)

    # Prepare multiple pages
    pages_to_create = [
        PageCreate(
            title=f"Tutorial - Chapter {i}",
            path=f"tutorials/chapter-{i}",
            content=f"# Chapter {i}\n\nContent for chapter {i}...",
            description=f"Tutorial chapter {i}",
            tags=["tutorial", f"chapter-{i}"],
            is_published=True
        )
        for i in range(1, 6)
    ]

    print(f"Creating {len(pages_to_create)} pages...")

    # Compare performance
    print("\nOLD WAY (one by one):")
    start = time.time()
    old_way_count = 0
    for page_data in pages_to_create[:2]:  # Just 2 for demo
        try:
            client.pages.create(page_data)
            old_way_count += 1
        except Exception as e:
            print(f"  Error: {e}")
    old_way_time = time.time() - start
    print(f"  Time: {old_way_time:.2f}s for {old_way_count} pages")
    print(f"  Average: {old_way_time/old_way_count:.2f}s per page")

    print("\nNEW WAY (batch):")
    start = time.time()
    try:
        created_pages = client.pages.create_many(pages_to_create)
        new_way_time = time.time() - start
        print(f"  Time: {new_way_time:.2f}s for {len(created_pages)} pages")
        print(f"  Average: {new_way_time/len(created_pages):.2f}s per page")
        print(f"  Speed improvement: {(old_way_time/old_way_count)/(new_way_time/len(created_pages)):.1f}x faster!")
    except APIError as e:
        print(f"  Batch creation error: {e}")
    print()

    # Example 2: Batch update pages
    print("2. Batch Update Pages")
    print("-" * 60)

    # Prepare updates
    updates = [
        {
            "id": 1,
            "content": "# Updated Chapter 1\n\nThis chapter has been updated!",
            "tags": ["tutorial", "chapter-1", "updated"]
        },
        {
            "id": 2,
            "title": "Tutorial - Chapter 2 (Revised)",
            "tags": ["tutorial", "chapter-2", "revised"]
        },
        {
            "id": 3,
            "is_published": False  # Unpublish chapter 3
        },
    ]

    print(f"Updating {len(updates)} pages...")
    try:
        updated_pages = client.pages.update_many(updates)
        print(f"  Successfully updated: {len(updated_pages)} pages")
        for page in updated_pages:
            print(f"    - {page.title} (ID: {page.id})")
    except APIError as e:
        print(f"  Update error: {e}")
    print()

    # Example 3: Batch delete pages
    print("3. Batch Delete Pages")
    print("-" * 60)

    page_ids = [1, 2, 3, 4, 5]
    print(f"Deleting {len(page_ids)} pages...")

    try:
        result = client.pages.delete_many(page_ids)
        print(f"  Successfully deleted: {result['successful']} pages")
        print(f"  Failed: {result['failed']} pages")

        if result['errors']:
            print("\n  Errors:")
            for error in result['errors']:
                print(f"    - Page {error['page_id']}: {error['error']}")
    except APIError as e:
        print(f"  Delete error: {e}")
    print()

    # Example 4: Partial failure handling
    print("4. Handling Partial Failures")
    print("-" * 60)

    # Some pages may fail to create
    mixed_pages = [
        PageCreate(title="Valid Page 1", path="valid-1", content="Content"),
        PageCreate(title="Valid Page 2", path="valid-2", content="Content"),
        PageCreate(title="", path="invalid", content=""),  # Invalid - empty title
    ]

    print(f"Attempting to create {len(mixed_pages)} pages (some invalid)...")
    try:
        pages = client.pages.create_many(mixed_pages)
        print(f"  All {len(pages)} pages created successfully!")
    except APIError as e:
        error_msg = str(e)
        if "Successfully created:" in error_msg:
            # Extract success count
            import re
            match = re.search(r"Successfully created: (\d+)", error_msg)
            if match:
                success_count = match.group(1)
                print(f"  Partial success: {success_count} pages created")
                print(f"  Some pages failed (see error details)")
        else:
            print(f"  Error: {error_msg}")
    print()

    # Example 5: Bulk content updates
    print("5. Bulk Content Updates")
    print("-" * 60)

    # Get all tutorial pages
    print("Finding tutorial pages...")
    tutorial_pages = client.pages.get_by_tags(["tutorial"], limit=10)
    print(f"  Found: {len(tutorial_pages)} tutorial pages")
    print()

    # Prepare updates for all
    print("Preparing bulk update...")
    updates = []
    for page in tutorial_pages:
        updates.append({
            "id": page.id,
            "content": page.content + "\n\n---\n*Last updated: 2025*",
            "tags": page.tags + ["2025-edition"]
        })

    print(f"Updating {len(updates)} pages with new footer...")
    try:
        updated = client.pages.update_many(updates)
        print(f"  Successfully updated: {len(updated)} pages")
    except APIError as e:
        print(f"  Update error: {e}")
    print()

    # Example 6: Data migration
    print("6. Data Migration Pattern")
    print("-" * 60)

    print("Migrating old format to new format...")

    # Get pages to migrate
    old_pages = client.pages.list(search="old-format", limit=5)
    print(f"  Found: {len(old_pages)} pages to migrate")

    # Prepare migration updates
    migration_updates = []
    for page in old_pages:
        # Transform content
        new_content = page.content.replace("==", "##")  # Example transformation
        new_content = new_content.replace("===", "###")

        migration_updates.append({
            "id": page.id,
            "content": new_content,
            "tags": page.tags + ["migrated"]
        })

    if migration_updates:
        print(f"  Migrating {len(migration_updates)} pages...")
        try:
            migrated = client.pages.update_many(migration_updates)
            print(f"  Successfully migrated: {len(migrated)} pages")
        except APIError as e:
            print(f"  Migration error: {e}")
    else:
        print("  No pages to migrate")
    print()

    # Example 7: Performance comparison
    print("7. Performance Comparison")
    print("-" * 60)

    test_pages = [
        PageCreate(
            title=f"Performance Test {i}",
            path=f"perf/test-{i}",
            content=f"Content {i}"
        )
        for i in range(10)
    ]

    # Sequential (old way)
    print("Sequential operations (old way):")
    seq_start = time.time()
    seq_count = 0
    for page_data in test_pages[:5]:  # Test with 5 pages
        try:
            client.pages.create(page_data)
            seq_count += 1
        except Exception:
            pass
    seq_time = time.time() - seq_start
    print(f"  Created {seq_count} pages in {seq_time:.2f}s")

    # Batch (new way)
    print("\nBatch operations (new way):")
    batch_start = time.time()
    try:
        batch_pages = client.pages.create_many(test_pages[5:])  # Other 5 pages
        batch_time = time.time() - batch_start
        print(f"  Created {len(batch_pages)} pages in {batch_time:.2f}s")
        print(f"\n  Performance improvement: {seq_time/batch_time:.1f}x faster!")
    except APIError as e:
        print(f"  Error: {e}")
    print()

    print("=" * 60)
    print("Batch operations example complete!")
    print("=" * 60)
    print("\nKey Takeaways:")
    print("  • Batch operations are significantly faster")
    print("  • Partial failures are handled gracefully")
    print("  • Network overhead is reduced")
    print("  • Perfect for bulk imports, migrations, and updates")


if __name__ == "__main__":
    main()
