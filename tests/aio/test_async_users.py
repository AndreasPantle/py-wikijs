"""Tests for async Users endpoint."""

from unittest.mock import AsyncMock, Mock

import pytest

from wikijs.aio.endpoints import AsyncUsersEndpoint
from wikijs.exceptions import APIError, ValidationError
from wikijs.models import User, UserCreate, UserUpdate


class TestAsyncUsersEndpoint:
    """Test AsyncUsersEndpoint class."""

    @pytest.fixture
    def client(self):
        """Create mock async client."""
        mock_client = Mock()
        mock_client.base_url = "https://wiki.example.com"
        mock_client._request = AsyncMock()
        return mock_client

    @pytest.fixture
    def endpoint(self, client):
        """Create AsyncUsersEndpoint instance."""
        return AsyncUsersEndpoint(client)

    @pytest.mark.asyncio
    async def test_list_users_minimal(self, endpoint):
        """Test listing users with minimal parameters."""
        # Mock response
        mock_response = {
            "data": {
                "users": {
                    "list": [
                        {
                            "id": 1,
                            "name": "John Doe",
                            "email": "john@example.com",
                            "providerKey": "local",
                            "isSystem": False,
                            "isActive": True,
                            "isVerified": True,
                            "location": None,
                            "jobTitle": None,
                            "timezone": None,
                            "createdAt": "2024-01-01T00:00:00Z",
                            "updatedAt": "2024-01-01T00:00:00Z",
                            "lastLoginAt": "2024-01-15T12:00:00Z",
                        }
                    ]
                }
            }
        }
        endpoint._post = AsyncMock(return_value=mock_response)

        # Call method
        users = await endpoint.list()

        # Verify
        assert len(users) == 1
        assert isinstance(users[0], User)
        assert users[0].id == 1
        assert users[0].name == "John Doe"
        assert users[0].email == "john@example.com"

        # Verify request
        endpoint._post.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_users_with_filters(self, endpoint):
        """Test listing users with filters."""
        mock_response = {"data": {"users": {"list": []}}}
        endpoint._post = AsyncMock(return_value=mock_response)

        # Call with filters
        users = await endpoint.list(
            limit=10,
            offset=5,
            search="john",
            order_by="email",
            order_direction="DESC",
        )

        # Verify
        assert users == []
        endpoint._post.assert_called_once()

    @pytest.mark.asyncio
    async def test_list_users_pagination(self, endpoint):
        """Test client-side pagination."""
        mock_response = {
            "data": {
                "users": {
                    "list": [
                        {
                            "id": i,
                            "name": f"User {i}",
                            "email": f"user{i}@example.com",
                            "providerKey": "local",
                            "isSystem": False,
                            "isActive": True,
                            "isVerified": True,
                            "location": None,
                            "jobTitle": None,
                            "timezone": None,
                            "createdAt": "2024-01-01T00:00:00Z",
                            "updatedAt": "2024-01-01T00:00:00Z",
                            "lastLoginAt": None,
                        }
                        for i in range(1, 11)
                    ]
                }
            }
        }
        endpoint._post = AsyncMock(return_value=mock_response)

        # Test offset
        users = await endpoint.list(offset=5)
        assert len(users) == 5
        assert users[0].id == 6

        # Test limit
        endpoint._post.reset_mock()
        endpoint._post.return_value = mock_response
        users = await endpoint.list(limit=3)
        assert len(users) == 3

        # Test both
        endpoint._post.reset_mock()
        endpoint._post.return_value = mock_response
        users = await endpoint.list(offset=2, limit=3)
        assert len(users) == 3
        assert users[0].id == 3

    @pytest.mark.asyncio
    async def test_list_users_validation_errors(self, endpoint):
        """Test validation errors in list."""
        # Invalid limit
        with pytest.raises(ValidationError) as exc_info:
            await endpoint.list(limit=0)
        assert "greater than 0" in str(exc_info.value)

        # Invalid offset
        with pytest.raises(ValidationError) as exc_info:
            await endpoint.list(offset=-1)
        assert "non-negative" in str(exc_info.value)

        # Invalid order_by
        with pytest.raises(ValidationError) as exc_info:
            await endpoint.list(order_by="invalid")
        assert "must be one of" in str(exc_info.value)

        # Invalid order_direction
        with pytest.raises(ValidationError) as exc_info:
            await endpoint.list(order_direction="INVALID")
        assert "must be ASC or DESC" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_list_users_api_error(self, endpoint):
        """Test API error handling in list."""
        mock_response = {"errors": [{"message": "GraphQL error"}]}
        endpoint._post = AsyncMock(return_value=mock_response)

        with pytest.raises(APIError) as exc_info:
            await endpoint.list()
        assert "GraphQL errors" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_user(self, endpoint):
        """Test getting a single user."""
        mock_response = {
            "data": {
                "users": {
                    "single": {
                        "id": 1,
                        "name": "John Doe",
                        "email": "john@example.com",
                        "providerKey": "local",
                        "isSystem": False,
                        "isActive": True,
                        "isVerified": True,
                        "location": "New York",
                        "jobTitle": "Developer",
                        "timezone": "America/New_York",
                        "groups": [
                            {"id": 1, "name": "Administrators"},
                            {"id": 2, "name": "Editors"},
                        ],
                        "createdAt": "2024-01-01T00:00:00Z",
                        "updatedAt": "2024-01-01T00:00:00Z",
                        "lastLoginAt": "2024-01-15T12:00:00Z",
                    }
                }
            }
        }
        endpoint._post = AsyncMock(return_value=mock_response)

        # Call method
        user = await endpoint.get(1)

        # Verify
        assert isinstance(user, User)
        assert user.id == 1
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.location == "New York"
        assert user.job_title == "Developer"
        assert len(user.groups) == 2
        assert user.groups[0].name == "Administrators"

    @pytest.mark.asyncio
    async def test_get_user_not_found(self, endpoint):
        """Test getting non-existent user."""
        mock_response = {"data": {"users": {"single": None}}}
        endpoint._post = AsyncMock(return_value=mock_response)

        with pytest.raises(APIError) as exc_info:
            await endpoint.get(999)
        assert "not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_user_validation_error(self, endpoint):
        """Test validation error in get."""
        with pytest.raises(ValidationError) as exc_info:
            await endpoint.get(0)
        assert "positive integer" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            await endpoint.get(-1)
        assert "positive integer" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            await endpoint.get("not-an-int")
        assert "positive integer" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_user_from_model(self, endpoint):
        """Test creating user from UserCreate model."""
        user_data = UserCreate(
            email="new@example.com",
            name="New User",
            password_raw="secret123",
            groups=[1, 2],
        )

        mock_response = {
            "data": {
                "users": {
                    "create": {
                        "responseResult": {
                            "succeeded": True,
                            "errorCode": 0,
                            "slug": "ok",
                            "message": "User created successfully",
                        },
                        "user": {
                            "id": 2,
                            "name": "New User",
                            "email": "new@example.com",
                            "providerKey": "local",
                            "isSystem": False,
                            "isActive": True,
                            "isVerified": False,
                            "location": None,
                            "jobTitle": None,
                            "timezone": None,
                            "createdAt": "2024-01-20T00:00:00Z",
                            "updatedAt": "2024-01-20T00:00:00Z",
                        },
                    }
                }
            }
        }
        endpoint._post = AsyncMock(return_value=mock_response)

        # Call method
        user = await endpoint.create(user_data)

        # Verify
        assert isinstance(user, User)
        assert user.id == 2
        assert user.name == "New User"
        assert user.email == "new@example.com"

        # Verify request
        endpoint._post.assert_called_once()
        call_args = endpoint._post.call_args
        assert call_args[1]["json_data"]["variables"]["email"] == "new@example.com"
        assert call_args[1]["json_data"]["variables"]["groups"] == [1, 2]

    @pytest.mark.asyncio
    async def test_create_user_from_dict(self, endpoint):
        """Test creating user from dictionary."""
        user_data = {
            "email": "new@example.com",
            "name": "New User",
            "password_raw": "secret123",
        }

        mock_response = {
            "data": {
                "users": {
                    "create": {
                        "responseResult": {"succeeded": True},
                        "user": {
                            "id": 2,
                            "name": "New User",
                            "email": "new@example.com",
                            "providerKey": "local",
                            "isSystem": False,
                            "isActive": True,
                            "isVerified": False,
                            "location": None,
                            "jobTitle": None,
                            "timezone": None,
                            "createdAt": "2024-01-20T00:00:00Z",
                            "updatedAt": "2024-01-20T00:00:00Z",
                        },
                    }
                }
            }
        }
        endpoint._post = AsyncMock(return_value=mock_response)

        # Call method
        user = await endpoint.create(user_data)

        # Verify
        assert isinstance(user, User)
        assert user.name == "New User"

    @pytest.mark.asyncio
    async def test_create_user_api_failure(self, endpoint):
        """Test API failure in create."""
        user_data = UserCreate(
            email="new@example.com", name="New User", password_raw="secret123"
        )

        mock_response = {
            "data": {
                "users": {
                    "create": {
                        "responseResult": {
                            "succeeded": False,
                            "message": "Email already exists",
                        }
                    }
                }
            }
        }
        endpoint._post = AsyncMock(return_value=mock_response)

        with pytest.raises(APIError) as exc_info:
            await endpoint.create(user_data)
        assert "Email already exists" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_user_validation_error(self, endpoint):
        """Test validation error in create."""
        # Invalid user data
        with pytest.raises(ValidationError):
            await endpoint.create({"email": "invalid"})

        # Wrong type
        with pytest.raises(ValidationError):
            await endpoint.create("not-a-dict-or-model")

    @pytest.mark.asyncio
    async def test_update_user_from_model(self, endpoint):
        """Test updating user from UserUpdate model."""
        user_data = UserUpdate(name="Updated Name", location="San Francisco")

        mock_response = {
            "data": {
                "users": {
                    "update": {
                        "responseResult": {"succeeded": True},
                        "user": {
                            "id": 1,
                            "name": "Updated Name",
                            "email": "john@example.com",
                            "providerKey": "local",
                            "isSystem": False,
                            "isActive": True,
                            "isVerified": True,
                            "location": "San Francisco",
                            "jobTitle": None,
                            "timezone": None,
                            "createdAt": "2024-01-01T00:00:00Z",
                            "updatedAt": "2024-01-20T00:00:00Z",
                        },
                    }
                }
            }
        }
        endpoint._post = AsyncMock(return_value=mock_response)

        # Call method
        user = await endpoint.update(1, user_data)

        # Verify
        assert isinstance(user, User)
        assert user.name == "Updated Name"
        assert user.location == "San Francisco"

        # Verify only non-None fields were sent
        call_args = endpoint._post.call_args
        variables = call_args[1]["json_data"]["variables"]
        assert "name" in variables
        assert "location" in variables
        assert "email" not in variables  # Not updated

    @pytest.mark.asyncio
    async def test_update_user_from_dict(self, endpoint):
        """Test updating user from dictionary."""
        user_data = {"name": "Updated Name"}

        mock_response = {
            "data": {
                "users": {
                    "update": {
                        "responseResult": {"succeeded": True},
                        "user": {
                            "id": 1,
                            "name": "Updated Name",
                            "email": "john@example.com",
                            "providerKey": "local",
                            "isSystem": False,
                            "isActive": True,
                            "isVerified": True,
                            "location": None,
                            "jobTitle": None,
                            "timezone": None,
                            "createdAt": "2024-01-01T00:00:00Z",
                            "updatedAt": "2024-01-20T00:00:00Z",
                        },
                    }
                }
            }
        }
        endpoint._post = AsyncMock(return_value=mock_response)

        # Call method
        user = await endpoint.update(1, user_data)

        # Verify
        assert user.name == "Updated Name"

    @pytest.mark.asyncio
    async def test_update_user_api_failure(self, endpoint):
        """Test API failure in update."""
        user_data = UserUpdate(name="Updated Name")

        mock_response = {
            "data": {
                "users": {
                    "update": {
                        "responseResult": {
                            "succeeded": False,
                            "message": "User not found",
                        }
                    }
                }
            }
        }
        endpoint._post = AsyncMock(return_value=mock_response)

        with pytest.raises(APIError) as exc_info:
            await endpoint.update(999, user_data)
        assert "User not found" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_user_validation_error(self, endpoint):
        """Test validation error in update."""
        # Invalid user ID
        with pytest.raises(ValidationError):
            await endpoint.update(0, UserUpdate(name="Test"))

        # Invalid user data
        with pytest.raises(ValidationError):
            await endpoint.update(1, {"name": ""})  # Empty name

        # Wrong type
        with pytest.raises(ValidationError):
            await endpoint.update(1, "not-a-dict-or-model")

    @pytest.mark.asyncio
    async def test_delete_user(self, endpoint):
        """Test deleting a user."""
        mock_response = {
            "data": {
                "users": {
                    "delete": {
                        "responseResult": {
                            "succeeded": True,
                            "message": "User deleted successfully",
                        }
                    }
                }
            }
        }
        endpoint._post = AsyncMock(return_value=mock_response)

        # Call method
        result = await endpoint.delete(1)

        # Verify
        assert result is True
        endpoint._post.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_user_api_failure(self, endpoint):
        """Test API failure in delete."""
        mock_response = {
            "data": {
                "users": {
                    "delete": {
                        "responseResult": {
                            "succeeded": False,
                            "message": "Cannot delete system user",
                        }
                    }
                }
            }
        }
        endpoint._post = AsyncMock(return_value=mock_response)

        with pytest.raises(APIError) as exc_info:
            await endpoint.delete(1)
        assert "Cannot delete system user" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_user_validation_error(self, endpoint):
        """Test validation error in delete."""
        with pytest.raises(ValidationError):
            await endpoint.delete(0)

        with pytest.raises(ValidationError):
            await endpoint.delete(-1)

        with pytest.raises(ValidationError):
            await endpoint.delete("not-an-int")

    @pytest.mark.asyncio
    async def test_search_users(self, endpoint):
        """Test searching users."""
        mock_response = {
            "data": {
                "users": {
                    "list": [
                        {
                            "id": 1,
                            "name": "John Doe",
                            "email": "john@example.com",
                            "providerKey": "local",
                            "isSystem": False,
                            "isActive": True,
                            "isVerified": True,
                            "location": None,
                            "jobTitle": None,
                            "timezone": None,
                            "createdAt": "2024-01-01T00:00:00Z",
                            "updatedAt": "2024-01-01T00:00:00Z",
                            "lastLoginAt": None,
                        }
                    ]
                }
            }
        }
        endpoint._post = AsyncMock(return_value=mock_response)

        # Call method
        users = await endpoint.search("john")

        # Verify
        assert len(users) == 1
        assert users[0].name == "John Doe"

    @pytest.mark.asyncio
    async def test_search_users_with_limit(self, endpoint):
        """Test searching users with limit."""
        mock_response = {"data": {"users": {"list": []}}}
        endpoint._post = AsyncMock(return_value=mock_response)

        users = await endpoint.search("test", limit=5)
        assert users == []

    @pytest.mark.asyncio
    async def test_search_users_validation_error(self, endpoint):
        """Test validation error in search."""
        # Empty query
        with pytest.raises(ValidationError):
            await endpoint.search("")

        # Non-string query
        with pytest.raises(ValidationError):
            await endpoint.search(123)

        # Invalid limit
        with pytest.raises(ValidationError):
            await endpoint.search("test", limit=0)

    @pytest.mark.asyncio
    async def test_normalize_user_data(self, endpoint):
        """Test user data normalization."""
        api_data = {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "providerKey": "local",
            "isSystem": False,
            "isActive": True,
            "isVerified": True,
            "location": "New York",
            "jobTitle": "Developer",
            "timezone": "America/New_York",
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-01T00:00:00Z",
            "lastLoginAt": "2024-01-15T12:00:00Z",
            "groups": [{"id": 1, "name": "Administrators"}],
        }

        normalized = endpoint._normalize_user_data(api_data)

        # Verify snake_case conversion
        assert normalized["id"] == 1
        assert normalized["name"] == "John Doe"
        assert normalized["email"] == "john@example.com"
        assert normalized["provider_key"] == "local"
        assert normalized["is_system"] is False
        assert normalized["is_active"] is True
        assert normalized["is_verified"] is True
        assert normalized["job_title"] == "Developer"
        assert normalized["last_login_at"] == "2024-01-15T12:00:00Z"
        assert len(normalized["groups"]) == 1
        assert normalized["groups"][0]["name"] == "Administrators"

    @pytest.mark.asyncio
    async def test_normalize_user_data_no_groups(self, endpoint):
        """Test normalization with no groups."""
        api_data = {
            "id": 1,
            "name": "John Doe",
            "email": "john@example.com",
            "providerKey": "local",
            "isSystem": False,
            "isActive": True,
            "isVerified": True,
            "location": None,
            "jobTitle": None,
            "timezone": None,
            "createdAt": "2024-01-01T00:00:00Z",
            "updatedAt": "2024-01-01T00:00:00Z",
            "lastLoginAt": None,
        }

        normalized = endpoint._normalize_user_data(api_data)
        assert normalized["groups"] == []
