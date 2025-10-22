# Users API Guide

Comprehensive guide for managing Wiki.js users through the SDK.

## Table of Contents

- [Overview](#overview)
- [User Models](#user-models)
- [Basic Operations](#basic-operations)
- [Async Operations](#async-operations)
- [Advanced Usage](#advanced-usage)
- [Error Handling](#error-handling)
- [Best Practices](#best-practices)

## Overview

The Users API provides complete user management capabilities for Wiki.js, including:

- **CRUD Operations**: Create, read, update, and delete users
- **User Search**: Find users by name or email
- **User Listing**: List all users with filtering and pagination
- **Group Management**: Assign users to groups
- **Profile Management**: Update user profiles and settings

Both **synchronous** and **asynchronous** clients are supported with identical interfaces.

## User Models

### User

Represents a complete Wiki.js user with all profile information.

```python
from wikijs.models import User

# User fields
user = User(
    id=1,
    name="John Doe",
    email="john@example.com",
    provider_key="local",          # Authentication provider
    is_system=False,               # System user flag
    is_active=True,                # Account active status
    is_verified=True,              # Email verified
    location="New York",           # Optional location
    job_title="Developer",         # Optional job title
    timezone="America/New_York",   # Optional timezone
    groups=[                       # User's groups
        {"id": 1, "name": "Administrators"},
        {"id": 2, "name": "Editors"}
    ],
    created_at="2024-01-01T00:00:00Z",
    updated_at="2024-01-01T00:00:00Z",
    last_login_at="2024-01-15T12:00:00Z"
)
```

### UserCreate

Model for creating new users.

```python
from wikijs.models import UserCreate

# Minimal user creation
new_user = UserCreate(
    email="newuser@example.com",
    name="New User",
    password_raw="SecurePassword123"
)

# Complete user creation
new_user = UserCreate(
    email="newuser@example.com",
    name="New User",
    password_raw="SecurePassword123",
    provider_key="local",          # Default: "local"
    groups=[1, 2],                 # Group IDs
    must_change_password=False,    # Force password change on first login
    send_welcome_email=True,       # Send welcome email
    location="San Francisco",
    job_title="Software Engineer",
    timezone="America/Los_Angeles"
)
```

**Validation Rules:**
- Email must be valid format
- Name must be 2-255 characters
- Password must be 6-255 characters
- Groups must be list of integer IDs

### UserUpdate

Model for updating existing users. All fields are optional.

```python
from wikijs.models import UserUpdate

# Partial update - only specified fields are changed
update_data = UserUpdate(
    name="Jane Doe",
    location="Los Angeles"
)

# Complete update
update_data = UserUpdate(
    name="Jane Doe",
    email="jane@example.com",
    password_raw="NewPassword123",
    location="Los Angeles",
    job_title="Senior Developer",
    timezone="America/Los_Angeles",
    groups=[1, 2, 3],              # Replace all groups
    is_active=True,
    is_verified=True
)
```

**Notes:**
- Only non-None fields are sent to the API
- Partial updates are fully supported
- Password is optional (only include if changing)

### UserGroup

Represents a user's group membership.

```python
from wikijs.models import UserGroup

group = UserGroup(
    id=1,
    name="Administrators"
)
```

## Basic Operations

### Synchronous Client

```python
from wikijs import WikiJSClient
from wikijs.models import UserCreate, UserUpdate

# Initialize client
client = WikiJSClient(
    base_url="https://wiki.example.com",
    auth="your-api-key"
)

# List all users
users = client.users.list()
for user in users:
    print(f"{user.name} ({user.email})")

# List with filtering
users = client.users.list(
    limit=10,
    offset=0,
    search="john",
    order_by="name",
    order_direction="ASC"
)

# Get a specific user
user = client.users.get(user_id=1)
print(f"User: {user.name}")
print(f"Email: {user.email}")
print(f"Groups: {[g.name for g in user.groups]}")

# Create a new user
new_user_data = UserCreate(
    email="newuser@example.com",
    name="New User",
    password_raw="SecurePassword123",
    groups=[1, 2]
)
created_user = client.users.create(new_user_data)
print(f"Created user: {created_user.id}")

# Update a user
update_data = UserUpdate(
    name="Updated Name",
    location="New Location"
)
updated_user = client.users.update(
    user_id=created_user.id,
    user_data=update_data
)

# Search for users
results = client.users.search("john", limit=5)
for user in results:
    print(f"Found: {user.name} ({user.email})")

# Delete a user
success = client.users.delete(user_id=created_user.id)
if success:
    print("User deleted successfully")
```

## Async Operations

### Async Client

```python
import asyncio
from wikijs.aio import AsyncWikiJSClient
from wikijs.models import UserCreate, UserUpdate

async def manage_users():
    # Initialize async client
    async with AsyncWikiJSClient(
        base_url="https://wiki.example.com",
        auth="your-api-key"
    ) as client:
        # List users
        users = await client.users.list()

        # Get specific user
        user = await client.users.get(user_id=1)

        # Create user
        new_user_data = UserCreate(
            email="newuser@example.com",
            name="New User",
            password_raw="SecurePassword123"
        )
        created_user = await client.users.create(new_user_data)

        # Update user
        update_data = UserUpdate(name="Updated Name")
        updated_user = await client.users.update(
            user_id=created_user.id,
            user_data=update_data
        )

        # Search users
        results = await client.users.search("john", limit=5)

        # Delete user
        success = await client.users.delete(user_id=created_user.id)

# Run async function
asyncio.run(manage_users())
```

### Concurrent Operations

Process multiple users concurrently for better performance:

```python
import asyncio
from wikijs.aio import AsyncWikiJSClient
from wikijs.models import UserUpdate

async def update_users_concurrently():
    async with AsyncWikiJSClient(
        base_url="https://wiki.example.com",
        auth="your-api-key"
    ) as client:
        # Get all users
        users = await client.users.list()

        # Update all users concurrently
        update_data = UserUpdate(is_verified=True)

        tasks = [
            client.users.update(user.id, update_data)
            for user in users
            if not user.is_verified
        ]

        # Execute all updates concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Process results
        success_count = sum(1 for r in results if not isinstance(r, Exception))
        print(f"Updated {success_count}/{len(tasks)} users")

asyncio.run(update_users_concurrently())
```

## Advanced Usage

### Using Dictionaries Instead of Models

You can use dictionaries instead of model objects:

```python
# Create user from dict
user_dict = {
    "email": "user@example.com",
    "name": "Test User",
    "password_raw": "SecurePassword123",
    "groups": [1, 2]
}
created_user = client.users.create(user_dict)

# Update user from dict
update_dict = {
    "name": "Updated Name",
    "location": "New Location"
}
updated_user = client.users.update(user_id=1, user_data=update_dict)
```

### Pagination

Handle large user lists with pagination:

```python
# Fetch users in batches
def fetch_all_users(client, batch_size=50):
    all_users = []
    offset = 0

    while True:
        batch = client.users.list(
            limit=batch_size,
            offset=offset,
            order_by="id",
            order_direction="ASC"
        )

        if not batch:
            break

        all_users.extend(batch)
        offset += batch_size

        print(f"Fetched {len(all_users)} users so far...")

    return all_users

# Async pagination
async def fetch_all_users_async(client, batch_size=50):
    all_users = []
    offset = 0

    while True:
        batch = await client.users.list(
            limit=batch_size,
            offset=offset,
            order_by="id",
            order_direction="ASC"
        )

        if not batch:
            break

        all_users.extend(batch)
        offset += batch_size

    return all_users
```

### Group Management

Manage user group assignments:

```python
from wikijs.models import UserUpdate

# Add user to groups
update_data = UserUpdate(groups=[1, 2, 3])  # Group IDs
updated_user = client.users.update(user_id=1, user_data=update_data)

# Remove user from all groups
update_data = UserUpdate(groups=[])
updated_user = client.users.update(user_id=1, user_data=update_data)

# Get user's current groups
user = client.users.get(user_id=1)
print("User groups:")
for group in user.groups:
    print(f"  - {group.name} (ID: {group.id})")
```

### Bulk User Creation

Create multiple users efficiently:

```python
from wikijs.models import UserCreate

# Sync bulk creation
def create_users_bulk(client, user_data_list):
    created_users = []

    for user_data in user_data_list:
        try:
            user = client.users.create(user_data)
            created_users.append(user)
            print(f"Created: {user.name}")
        except Exception as e:
            print(f"Failed to create {user_data['name']}: {e}")

    return created_users

# Async bulk creation (concurrent)
async def create_users_bulk_async(client, user_data_list):
    tasks = [
        client.users.create(user_data)
        for user_data in user_data_list
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    created_users = [
        r for r in results if not isinstance(r, Exception)
    ]

    print(f"Created {len(created_users)}/{len(user_data_list)} users")
    return created_users
```

## Error Handling

### Common Exceptions

```python
from wikijs.exceptions import (
    ValidationError,
    APIError,
    AuthenticationError,
    ConnectionError,
    TimeoutError
)

try:
    # Create user with invalid data
    user_data = UserCreate(
        email="invalid-email",  # Invalid format
        name="Test",
        password_raw="123"      # Too short
    )
except ValidationError as e:
    print(f"Validation error: {e}")

try:
    # Get non-existent user
    user = client.users.get(user_id=99999)
except APIError as e:
    print(f"API error: {e}")

try:
    # Invalid authentication
    client = WikiJSClient(
        base_url="https://wiki.example.com",
        auth="invalid-key"
    )
    users = client.users.list()
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
```

### Robust Error Handling

```python
from wikijs.exceptions import ValidationError, APIError

def create_user_safely(client, user_data):
    """Create user with comprehensive error handling."""
    try:
        # Validate data first
        validated_data = UserCreate(**user_data)

        # Create user
        user = client.users.create(validated_data)
        print(f"✓ Created user: {user.name} (ID: {user.id})")
        return user

    except ValidationError as e:
        print(f"✗ Validation error: {e}")
        # Handle validation errors (e.g., fix data and retry)
        return None

    except APIError as e:
        if "already exists" in str(e).lower():
            print(f"✗ User already exists: {user_data['email']}")
            # Handle duplicate user
            return None
        else:
            print(f"✗ API error: {e}")
            raise

    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        raise

# Async version
async def create_user_safely_async(client, user_data):
    try:
        validated_data = UserCreate(**user_data)
        user = await client.users.create(validated_data)
        print(f"✓ Created user: {user.name} (ID: {user.id})")
        return user
    except ValidationError as e:
        print(f"✗ Validation error: {e}")
        return None
    except APIError as e:
        if "already exists" in str(e).lower():
            print(f"✗ User already exists: {user_data['email']}")
            return None
        else:
            print(f"✗ API error: {e}")
            raise
```

## Best Practices

### 1. Use Models for Type Safety

Always use Pydantic models for better validation and IDE support:

```python
# Good - type safe with validation
user_data = UserCreate(
    email="user@example.com",
    name="Test User",
    password_raw="SecurePassword123"
)
user = client.users.create(user_data)

# Acceptable - but less type safe
user_dict = {
    "email": "user@example.com",
    "name": "Test User",
    "password_raw": "SecurePassword123"
}
user = client.users.create(user_dict)
```

### 2. Handle Pagination for Large Datasets

Always paginate when dealing with many users:

```python
# Good - paginated
all_users = []
offset = 0
batch_size = 50

while True:
    batch = client.users.list(limit=batch_size, offset=offset)
    if not batch:
        break
    all_users.extend(batch)
    offset += batch_size

# Bad - loads all users at once
all_users = client.users.list()  # May be slow for large user bases
```

### 3. Use Async for Concurrent Operations

Use async client for better performance when processing multiple users:

```python
# Good - concurrent async operations
async with AsyncWikiJSClient(...) as client:
    tasks = [client.users.get(id) for id in user_ids]
    users = await asyncio.gather(*tasks)

# Less efficient - sequential sync operations
for user_id in user_ids:
    user = client.users.get(user_id)
```

### 4. Validate Before API Calls

Catch validation errors early:

```python
# Good - validate first
try:
    user_data = UserCreate(**raw_data)
    user = client.users.create(user_data)
except ValidationError as e:
    print(f"Invalid data: {e}")
    # Fix data before API call

# Less efficient - validation happens during API call
user = client.users.create(raw_data)
```

### 5. Use Partial Updates

Only update fields that changed:

```python
# Good - only update changed fields
update_data = UserUpdate(name="New Name")
user = client.users.update(user_id=1, user_data=update_data)

# Wasteful - updates all fields
update_data = UserUpdate(
    name="New Name",
    email=user.email,
    location=user.location,
    # ... all other fields
)
user = client.users.update(user_id=1, user_data=update_data)
```

### 6. Implement Retry Logic for Production

```python
import time
from wikijs.exceptions import ConnectionError, TimeoutError

def create_user_with_retry(client, user_data, max_retries=3):
    """Create user with automatic retry on transient failures."""
    for attempt in range(max_retries):
        try:
            return client.users.create(user_data)
        except (ConnectionError, TimeoutError) as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Retry {attempt + 1}/{max_retries} after {wait_time}s...")
                time.sleep(wait_time)
            else:
                raise
```

### 7. Secure Password Handling

```python
import getpass
from wikijs.models import UserCreate

# Good - prompt for password securely
password = getpass.getpass("Enter password: ")
user_data = UserCreate(
    email="user@example.com",
    name="Test User",
    password_raw=password
)

# Bad - hardcoded passwords
user_data = UserCreate(
    email="user@example.com",
    name="Test User",
    password_raw="password123"  # Never do this!
)
```

## Examples

See the `examples/` directory for complete working examples:

- `examples/users_basic.py` - Basic user management operations
- `examples/users_async.py` - Async user management with concurrency
- `examples/users_bulk_import.py` - Bulk user import from CSV

## API Reference

### UsersEndpoint / AsyncUsersEndpoint

#### `list(limit=None, offset=None, search=None, order_by="name", order_direction="ASC")`

List users with optional filtering and pagination.

**Parameters:**
- `limit` (int, optional): Maximum number of users to return
- `offset` (int, optional): Number of users to skip
- `search` (str, optional): Search term (filters by name or email)
- `order_by` (str): Field to sort by (`name`, `email`, `createdAt`, `lastLoginAt`)
- `order_direction` (str): Sort direction (`ASC` or `DESC`)

**Returns:** `List[User]`

**Raises:** `ValidationError`, `APIError`

#### `get(user_id)`

Get a specific user by ID.

**Parameters:**
- `user_id` (int): User ID

**Returns:** `User`

**Raises:** `ValidationError`, `APIError`

#### `create(user_data)`

Create a new user.

**Parameters:**
- `user_data` (UserCreate or dict): User creation data

**Returns:** `User`

**Raises:** `ValidationError`, `APIError`

#### `update(user_id, user_data)`

Update an existing user.

**Parameters:**
- `user_id` (int): User ID
- `user_data` (UserUpdate or dict): User update data

**Returns:** `User`

**Raises:** `ValidationError`, `APIError`

#### `delete(user_id)`

Delete a user.

**Parameters:**
- `user_id` (int): User ID

**Returns:** `bool` (True if successful)

**Raises:** `ValidationError`, `APIError`

#### `search(query, limit=None)`

Search for users by name or email.

**Parameters:**
- `query` (str): Search query
- `limit` (int, optional): Maximum number of results

**Returns:** `List[User]`

**Raises:** `ValidationError`, `APIError`

## Related Documentation

- [Async Usage Guide](async_usage.md)
- [Authentication Guide](../README.md#authentication)
- [API Reference](../README.md#api-documentation)
- [Examples](../examples/)

## Support

For issues and questions:
- GitHub Issues: [wikijs-python-sdk/issues](https://github.com/yourusername/wikijs-python-sdk/issues)
- Documentation: [Full Documentation](../README.md)
