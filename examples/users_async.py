"""Async users management example for wikijs-python-sdk.

This example demonstrates:
- Async user operations
- Concurrent user processing
- Bulk operations with asyncio.gather
- Performance comparison with sync operations
"""

import asyncio
import time
from typing import List

from wikijs.aio import AsyncWikiJSClient
from wikijs.exceptions import APIError, ValidationError
from wikijs.models import User, UserCreate, UserUpdate


async def basic_async_operations():
    """Demonstrate basic async user operations."""
    print("=" * 60)
    print("Async Users API - Basic Operations")
    print("=" * 60)

    # Initialize async client with context manager
    async with AsyncWikiJSClient(
        base_url="https://wiki.example.com", auth="your-api-key-here"
    ) as client:

        # 1. List users
        print("\n1. Listing all users...")
        try:
            users = await client.users.list()
            print(f"   Found {len(users)} users")
            for user in users[:5]:
                print(f"   - {user.name} ({user.email})")
        except APIError as e:
            print(f"   Error: {e}")

        # 2. Search users
        print("\n2. Searching for users...")
        try:
            results = await client.users.search("admin", limit=5)
            print(f"   Found {len(results)} matching users")
        except APIError as e:
            print(f"   Error: {e}")

        # 3. Create user
        print("\n3. Creating a new user...")
        try:
            new_user_data = UserCreate(
                email="asynctest@example.com",
                name="Async Test User",
                password_raw="SecurePassword123",
                location="Remote",
                job_title="Engineer",
            )

            created_user = await client.users.create(new_user_data)
            print(f"   ✓ Created: {created_user.name} (ID: {created_user.id})")
            test_user_id = created_user.id

        except (ValidationError, APIError) as e:
            print(f"   ✗ Error: {e}")
            return

        # 4. Get user
        print(f"\n4. Getting user {test_user_id}...")
        try:
            user = await client.users.get(test_user_id)
            print(f"   User: {user.name}")
            print(f"   Email: {user.email}")
            print(f"   Location: {user.location}")
        except APIError as e:
            print(f"   Error: {e}")

        # 5. Update user
        print(f"\n5. Updating user...")
        try:
            update_data = UserUpdate(
                name="Updated Async User", location="San Francisco"
            )
            updated_user = await client.users.update(test_user_id, update_data)
            print(f"   ✓ Updated: {updated_user.name}")
            print(f"     Location: {updated_user.location}")
        except APIError as e:
            print(f"   Error: {e}")

        # 6. Delete user
        print(f"\n6. Deleting test user...")
        try:
            await client.users.delete(test_user_id)
            print(f"   ✓ User deleted")
        except APIError as e:
            print(f"   Error: {e}")


async def concurrent_user_fetch():
    """Demonstrate concurrent user fetching for better performance."""
    print("\n" + "=" * 60)
    print("Concurrent User Fetching")
    print("=" * 60)

    async with AsyncWikiJSClient(
        base_url="https://wiki.example.com", auth="your-api-key-here"
    ) as client:

        # Get list of user IDs
        print("\n1. Getting list of users...")
        users = await client.users.list(limit=10)
        user_ids = [user.id for user in users]
        print(f"   Will fetch {len(user_ids)} users concurrently")

        # Fetch all users concurrently
        print("\n2. Fetching users concurrently...")
        start_time = time.time()

        tasks = [client.users.get(user_id) for user_id in user_ids]
        fetched_users = await asyncio.gather(*tasks, return_exceptions=True)

        elapsed = time.time() - start_time

        # Process results
        successful = [u for u in fetched_users if isinstance(u, User)]
        failed = [u for u in fetched_users if isinstance(u, Exception)]

        print(f"   ✓ Fetched {len(successful)} users successfully")
        print(f"   ✗ Failed: {len(failed)}")
        print(f"   ⏱  Time: {elapsed:.2f}s")
        print(f"   📊 Average: {elapsed/len(user_ids):.3f}s per user")


async def bulk_user_creation():
    """Demonstrate bulk user creation with concurrent operations."""
    print("\n" + "=" * 60)
    print("Bulk User Creation (Concurrent)")
    print("=" * 60)

    async with AsyncWikiJSClient(
        base_url="https://wiki.example.com", auth="your-api-key-here"
    ) as client:

        # Prepare user data
        print("\n1. Preparing user data...")
        users_to_create = [
            UserCreate(
                email=f"bulkuser{i}@example.com",
                name=f"Bulk User {i}",
                password_raw=f"SecurePass{i}123",
                location="Test Location",
                job_title="Test Engineer",
            )
            for i in range(1, 6)
        ]
        print(f"   Prepared {len(users_to_create)} users")

        # Create all users concurrently
        print("\n2. Creating users concurrently...")
        start_time = time.time()

        tasks = [client.users.create(user_data) for user_data in users_to_create]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        elapsed = time.time() - start_time

        # Process results
        created_users = [r for r in results if isinstance(r, User)]
        failed = [r for r in results if isinstance(r, Exception)]

        print(f"   ✓ Created: {len(created_users)} users")
        print(f"   ✗ Failed: {len(failed)}")
        print(f"   ⏱  Time: {elapsed:.2f}s")

        # Show created users
        for user in created_users:
            print(f"     - {user.name} (ID: {user.id})")

        # Update all users concurrently
        if created_users:
            print("\n3. Updating all users concurrently...")
            update_data = UserUpdate(location="Updated Location", is_verified=True)

            tasks = [
                client.users.update(user.id, update_data) for user in created_users
            ]
            updated_users = await asyncio.gather(*tasks, return_exceptions=True)

            successful_updates = [u for u in updated_users if isinstance(u, User)]
            print(f"   ✓ Updated: {len(successful_updates)} users")

        # Delete all test users
        if created_users:
            print("\n4. Cleaning up (deleting test users)...")
            tasks = [client.users.delete(user.id) for user in created_users]
            results = await asyncio.gather(*tasks, return_exceptions=True)

            successful_deletes = [r for r in results if r is True]
            print(f"   ✓ Deleted: {len(successful_deletes)} users")


async def performance_comparison():
    """Compare sync vs async performance."""
    print("\n" + "=" * 60)
    print("Performance Comparison: Sync vs Async")
    print("=" * 60)

    async with AsyncWikiJSClient(
        base_url="https://wiki.example.com", auth="your-api-key-here"
    ) as async_client:

        # Get list of user IDs
        users = await async_client.users.list(limit=20)
        user_ids = [user.id for user in users[:10]]  # Use first 10

        print(f"\nFetching {len(user_ids)} users...")

        # Async concurrent fetching
        print("\n1. Async (concurrent):")
        start_time = time.time()

        tasks = [async_client.users.get(user_id) for user_id in user_ids]
        async_results = await asyncio.gather(*tasks, return_exceptions=True)

        async_time = time.time() - start_time

        async_successful = len([r for r in async_results if isinstance(r, User)])
        print(f"   Fetched: {async_successful} users")
        print(f"   Time: {async_time:.2f}s")
        print(f"   Rate: {len(user_ids)/async_time:.1f} users/sec")

        # Async sequential fetching (for comparison)
        print("\n2. Async (sequential):")
        start_time = time.time()

        sequential_results = []
        for user_id in user_ids:
            try:
                user = await async_client.users.get(user_id)
                sequential_results.append(user)
            except Exception as e:
                sequential_results.append(e)

        sequential_time = time.time() - start_time

        seq_successful = len([r for r in sequential_results if isinstance(r, User)])
        print(f"   Fetched: {seq_successful} users")
        print(f"   Time: {sequential_time:.2f}s")
        print(f"   Rate: {len(user_ids)/sequential_time:.1f} users/sec")

        # Calculate speedup
        speedup = sequential_time / async_time
        print(f"\n📊 Performance Summary:")
        print(f"   Concurrent speedup: {speedup:.1f}x faster")
        print(f"   Time saved: {sequential_time - async_time:.2f}s")


async def batch_user_updates():
    """Demonstrate batch updates with progress tracking."""
    print("\n" + "=" * 60)
    print("Batch User Updates with Progress Tracking")
    print("=" * 60)

    async with AsyncWikiJSClient(
        base_url="https://wiki.example.com", auth="your-api-key-here"
    ) as client:

        # Get users to update
        print("\n1. Finding users to update...")
        users = await client.users.list(limit=10)
        print(f"   Found {len(users)} users")

        # Update all users concurrently with progress
        print("\n2. Updating users...")
        update_data = UserUpdate(is_verified=True)

        async def update_with_progress(user: User, index: int, total: int):
            """Update user and show progress."""
            try:
                updated = await client.users.update(user.id, update_data)
                print(f"   [{index}/{total}] ✓ Updated: {updated.name}")
                return updated
            except Exception as e:
                print(f"   [{index}/{total}] ✗ Failed: {user.name} - {e}")
                return e

        tasks = [
            update_with_progress(user, i + 1, len(users))
            for i, user in enumerate(users)
        ]

        results = await asyncio.gather(*tasks)

        # Summary
        successful = len([r for r in results if isinstance(r, User)])
        failed = len([r for r in results if isinstance(r, Exception)])

        print(f"\n   Summary:")
        print(f"   ✓ Successful: {successful}")
        print(f"   ✗ Failed: {failed}")


async def advanced_error_handling():
    """Demonstrate advanced error handling patterns."""
    print("\n" + "=" * 60)
    print("Advanced Error Handling")
    print("=" * 60)

    async with AsyncWikiJSClient(
        base_url="https://wiki.example.com", auth="your-api-key-here"
    ) as client:

        print("\n1. Individual error handling:")

        # Try to create multiple users with mixed valid/invalid data
        test_users = [
            {
                "email": "valid1@example.com",
                "name": "Valid User 1",
                "password_raw": "SecurePass123",
            },
            {
                "email": "invalid-email",
                "name": "Invalid Email",
                "password_raw": "SecurePass123",
            },
            {
                "email": "valid2@example.com",
                "name": "Valid User 2",
                "password_raw": "123",
            },  # Weak password
            {
                "email": "valid3@example.com",
                "name": "Valid User 3",
                "password_raw": "SecurePass123",
            },
        ]

        async def create_user_safe(user_data: dict):
            """Create user with error handling."""
            try:
                validated_data = UserCreate(**user_data)
                user = await client.users.create(validated_data)
                print(f"   ✓ Created: {user.name}")
                return user
            except ValidationError as e:
                print(f"   ✗ Validation error for {user_data.get('email')}: {e}")
                return None
            except APIError as e:
                print(f"   ✗ API error for {user_data.get('email')}: {e}")
                return None

        results = await asyncio.gather(*[create_user_safe(u) for u in test_users])

        # Clean up created users
        created = [r for r in results if r is not None]
        if created:
            print(f"\n2. Cleaning up {len(created)} created users...")
            await asyncio.gather(*[client.users.delete(u.id) for u in created])
            print("   ✓ Cleanup complete")


async def main():
    """Run all async examples."""
    try:
        # Basic operations
        await basic_async_operations()

        # Concurrent operations
        await concurrent_user_fetch()

        # Bulk operations
        await bulk_user_creation()

        # Performance comparison
        await performance_comparison()

        # Batch updates
        await batch_user_updates()

        # Error handling
        await advanced_error_handling()

        print("\n" + "=" * 60)
        print("All examples completed!")
        print("=" * 60)

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Run all examples
    asyncio.run(main())
