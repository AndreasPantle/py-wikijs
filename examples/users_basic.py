"""Basic users management example for wikijs-python-sdk.

This example demonstrates:
- Creating users
- Reading user information
- Updating users
- Deleting users
- Searching users
- Managing user groups
"""

from wikijs import WikiJSClient
from wikijs.exceptions import APIError, ValidationError
from wikijs.models import UserCreate, UserUpdate


def main():
    """Run basic user management operations."""
    # Initialize client
    client = WikiJSClient(
        base_url="https://wiki.example.com",
        auth="your-api-key-here",  # Replace with your actual API key
    )

    print("=" * 60)
    print("Wiki.js Users API - Basic Operations Example")
    print("=" * 60)

    # 1. List all users
    print("\n1. Listing all users...")
    try:
        users = client.users.list()
        print(f"   Found {len(users)} users")
        for user in users[:5]:  # Show first 5
            print(f"   - {user.name} ({user.email}) - Active: {user.is_active}")
    except APIError as e:
        print(f"   Error listing users: {e}")

    # 2. List users with filtering
    print("\n2. Listing users with pagination and ordering...")
    try:
        users = client.users.list(
            limit=10, offset=0, order_by="email", order_direction="ASC"
        )
        print(f"   Found {len(users)} users (first 10)")
    except APIError as e:
        print(f"   Error: {e}")

    # 3. Search for users
    print("\n3. Searching for users...")
    try:
        search_term = "admin"
        results = client.users.search(search_term, limit=5)
        print(f"   Found {len(results)} users matching '{search_term}'")
        for user in results:
            print(f"   - {user.name} ({user.email})")
    except APIError as e:
        print(f"   Error searching: {e}")

    # 4. Create a new user
    print("\n4. Creating a new user...")
    try:
        new_user_data = UserCreate(
            email="testuser@example.com",
            name="Test User",
            password_raw="SecurePassword123",
            groups=[1],  # Assign to group with ID 1
            location="San Francisco",
            job_title="QA Engineer",
            timezone="America/Los_Angeles",
            send_welcome_email=False,  # Don't send email for test user
            must_change_password=True,
        )

        created_user = client.users.create(new_user_data)
        print(f"   ✓ Created user: {created_user.name}")
        print(f"     ID: {created_user.id}")
        print(f"     Email: {created_user.email}")
        print(f"     Active: {created_user.is_active}")
        print(f"     Verified: {created_user.is_verified}")

        # Save user ID for later operations
        test_user_id = created_user.id

    except ValidationError as e:
        print(f"   ✗ Validation error: {e}")
        return
    except APIError as e:
        print(f"   ✗ API error: {e}")
        if "already exists" in str(e).lower():
            print("   Note: User might already exist from previous run")
        return

    # 5. Get specific user
    print(f"\n5. Getting user by ID ({test_user_id})...")
    try:
        user = client.users.get(test_user_id)
        print(f"   User: {user.name}")
        print(f"   Email: {user.email}")
        print(f"   Location: {user.location}")
        print(f"   Job Title: {user.job_title}")
        print(f"   Groups: {[g.name for g in user.groups]}")
    except APIError as e:
        print(f"   Error: {e}")

    # 6. Update user information
    print(f"\n6. Updating user...")
    try:
        update_data = UserUpdate(
            name="Updated Test User",
            location="New York",
            job_title="Senior QA Engineer",
            is_verified=True,
        )

        updated_user = client.users.update(test_user_id, update_data)
        print(f"   ✓ Updated user: {updated_user.name}")
        print(f"     New location: {updated_user.location}")
        print(f"     New job title: {updated_user.job_title}")
        print(f"     Verified: {updated_user.is_verified}")
    except APIError as e:
        print(f"   Error: {e}")

    # 7. Update user password
    print(f"\n7. Updating user password...")
    try:
        password_update = UserUpdate(password_raw="NewSecurePassword456")

        updated_user = client.users.update(test_user_id, password_update)
        print(f"   ✓ Password updated for user: {updated_user.name}")
    except APIError as e:
        print(f"   Error: {e}")

    # 8. Manage user groups
    print(f"\n8. Managing user groups...")
    try:
        # Add user to multiple groups
        group_update = UserUpdate(groups=[1, 2, 3])
        updated_user = client.users.update(test_user_id, group_update)
        print(f"   ✓ User groups updated")
        print(f"     Groups: {[g.name for g in updated_user.groups]}")
    except APIError as e:
        print(f"   Error: {e}")

    # 9. Deactivate user
    print(f"\n9. Deactivating user...")
    try:
        deactivate_update = UserUpdate(is_active=False)
        updated_user = client.users.update(test_user_id, deactivate_update)
        print(f"   ✓ User deactivated: {updated_user.name}")
        print(f"     Active: {updated_user.is_active}")
    except APIError as e:
        print(f"   Error: {e}")

    # 10. Reactivate user
    print(f"\n10. Reactivating user...")
    try:
        reactivate_update = UserUpdate(is_active=True)
        updated_user = client.users.update(test_user_id, reactivate_update)
        print(f"   ✓ User reactivated: {updated_user.name}")
        print(f"     Active: {updated_user.is_active}")
    except APIError as e:
        print(f"   Error: {e}")

    # 11. Delete user
    print(f"\n11. Deleting test user...")
    try:
        success = client.users.delete(test_user_id)
        if success:
            print(f"   ✓ User deleted successfully")
    except APIError as e:
        print(f"   Error: {e}")
        if "system user" in str(e).lower():
            print("   Note: Cannot delete system users")

    # 12. Demonstrate error handling
    print("\n12. Demonstrating error handling...")

    # Try to create user with invalid email
    print("   a) Invalid email validation:")
    try:
        invalid_user = UserCreate(
            email="not-an-email", name="Test", password_raw="password123"
        )
        client.users.create(invalid_user)
    except ValidationError as e:
        print(f"      ✓ Caught validation error: {e}")

    # Try to create user with weak password
    print("   b) Weak password validation:")
    try:
        weak_password_user = UserCreate(
            email="test@example.com", name="Test User", password_raw="123"  # Too short
        )
        client.users.create(weak_password_user)
    except ValidationError as e:
        print(f"      ✓ Caught validation error: {e}")

    # Try to get non-existent user
    print("   c) Non-existent user:")
    try:
        user = client.users.get(99999)
    except APIError as e:
        print(f"      ✓ Caught API error: {e}")

    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)


def demonstrate_bulk_operations():
    """Demonstrate bulk user operations."""
    client = WikiJSClient(base_url="https://wiki.example.com", auth="your-api-key-here")

    print("\n" + "=" * 60)
    print("Bulk Operations Example")
    print("=" * 60)

    # Create multiple users
    print("\n1. Creating multiple users...")
    users_to_create = [
        {
            "email": f"user{i}@example.com",
            "name": f"User {i}",
            "password_raw": f"SecurePass{i}123",
            "job_title": "Team Member",
        }
        for i in range(1, 4)
    ]

    created_users = []
    for user_data in users_to_create:
        try:
            user = client.users.create(UserCreate(**user_data))
            created_users.append(user)
            print(f"   ✓ Created: {user.name}")
        except (ValidationError, APIError) as e:
            print(f"   ✗ Failed to create {user_data['name']}: {e}")

    # Update all created users
    print("\n2. Updating all created users...")
    update_data = UserUpdate(location="Team Location", is_verified=True)

    for user in created_users:
        try:
            updated_user = client.users.update(user.id, update_data)
            print(f"   ✓ Updated: {updated_user.name}")
        except APIError as e:
            print(f"   ✗ Failed to update {user.name}: {e}")

    # Delete all created users
    print("\n3. Cleaning up (deleting test users)...")
    for user in created_users:
        try:
            client.users.delete(user.id)
            print(f"   ✓ Deleted: {user.name}")
        except APIError as e:
            print(f"   ✗ Failed to delete {user.name}: {e}")


def demonstrate_pagination():
    """Demonstrate pagination for large user lists."""
    client = WikiJSClient(base_url="https://wiki.example.com", auth="your-api-key-here")

    print("\n" + "=" * 60)
    print("Pagination Example")
    print("=" * 60)

    # Fetch all users in batches
    print("\nFetching all users in batches of 50...")
    all_users = []
    offset = 0
    batch_size = 50

    while True:
        try:
            batch = client.users.list(
                limit=batch_size, offset=offset, order_by="id", order_direction="ASC"
            )

            if not batch:
                break

            all_users.extend(batch)
            offset += batch_size
            print(f"   Fetched batch: {len(batch)} users (total: {len(all_users)})")

        except APIError as e:
            print(f"   Error fetching batch: {e}")
            break

    print(f"\nTotal users fetched: {len(all_users)}")


if __name__ == "__main__":
    # Run main example
    main()

    # Uncomment to run additional examples:
    # demonstrate_bulk_operations()
    # demonstrate_pagination()
