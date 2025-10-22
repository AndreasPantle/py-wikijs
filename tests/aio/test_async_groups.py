"""Tests for async Groups endpoint."""

from unittest.mock import AsyncMock, Mock

import pytest

from wikijs.aio.endpoints import AsyncGroupsEndpoint
from wikijs.exceptions import APIError, ValidationError
from wikijs.models import Group, GroupCreate, GroupUpdate


class TestAsyncGroupsEndpoint:
    """Test AsyncGroupsEndpoint class."""

    @pytest.fixture
    def client(self):
        """Create mock async client."""
        mock_client = Mock()
        mock_client.base_url = "https://wiki.example.com"
        mock_client._request = AsyncMock()
        return mock_client

    @pytest.fixture
    def endpoint(self, client):
        """Create AsyncGroupsEndpoint instance."""
        return AsyncGroupsEndpoint(client)

    @pytest.mark.asyncio
    async def test_list_groups(self, endpoint):
        """Test listing groups."""
        mock_response = {
            "data": {
                "groups": {
                    "list": [
                        {
                            "id": 1,
                            "name": "Administrators",
                            "isSystem": False,
                            "redirectOnLogin": "/",
                            "permissions": ["manage:system"],
                            "pageRules": [],
                            "users": [],
                            "createdAt": "2024-01-01T00:00:00Z",
                            "updatedAt": "2024-01-01T00:00:00Z",
                        }
                    ]
                }
            }
        }
        endpoint._post = AsyncMock(return_value=mock_response)

        groups = await endpoint.list()

        assert len(groups) == 1
        assert isinstance(groups[0], Group)
        assert groups[0].name == "Administrators"

    @pytest.mark.asyncio
    async def test_get_group(self, endpoint):
        """Test getting a group."""
        mock_response = {
            "data": {
                "groups": {
                    "single": {
                        "id": 1,
                        "name": "Administrators",
                        "isSystem": False,
                        "redirectOnLogin": "/",
                        "permissions": ["manage:system"],
                        "pageRules": [],
                        "users": [{"id": 1, "name": "Admin", "email": "admin@example.com"}],
                        "createdAt": "2024-01-01T00:00:00Z",
                        "updatedAt": "2024-01-01T00:00:00Z",
                    }
                }
            }
        }
        endpoint._post = AsyncMock(return_value=mock_response)

        group = await endpoint.get(1)

        assert isinstance(group, Group)
        assert group.id == 1
        assert len(group.users) == 1

    @pytest.mark.asyncio
    async def test_create_group(self, endpoint):
        """Test creating a group."""
        group_data = GroupCreate(name="Editors", permissions=["read:pages"])

        mock_response = {
            "data": {
                "groups": {
                    "create": {
                        "responseResult": {"succeeded": True},
                        "group": {
                            "id": 2,
                            "name": "Editors",
                            "isSystem": False,
                            "redirectOnLogin": "/",
                            "permissions": ["read:pages"],
                            "pageRules": [],
                            "createdAt": "2024-01-01T00:00:00Z",
                            "updatedAt": "2024-01-01T00:00:00Z",
                        },
                    }
                }
            }
        }
        endpoint._post = AsyncMock(return_value=mock_response)

        group = await endpoint.create(group_data)

        assert isinstance(group, Group)
        assert group.name == "Editors"

    @pytest.mark.asyncio
    async def test_update_group(self, endpoint):
        """Test updating a group."""
        update_data = GroupUpdate(name="Senior Editors")

        mock_response = {
            "data": {
                "groups": {
                    "update": {
                        "responseResult": {"succeeded": True},
                        "group": {
                            "id": 1,
                            "name": "Senior Editors",
                            "isSystem": False,
                            "redirectOnLogin": "/",
                            "permissions": [],
                            "pageRules": [],
                            "createdAt": "2024-01-01T00:00:00Z",
                            "updatedAt": "2024-01-02T00:00:00Z",
                        },
                    }
                }
            }
        }
        endpoint._post = AsyncMock(return_value=mock_response)

        group = await endpoint.update(1, update_data)

        assert group.name == "Senior Editors"

    @pytest.mark.asyncio
    async def test_delete_group(self, endpoint):
        """Test deleting a group."""
        mock_response = {
            "data": {
                "groups": {
                    "delete": {
                        "responseResult": {"succeeded": True}
                    }
                }
            }
        }
        endpoint._post = AsyncMock(return_value=mock_response)

        result = await endpoint.delete(1)

        assert result is True

    @pytest.mark.asyncio
    async def test_assign_user(self, endpoint):
        """Test assigning a user to a group."""
        mock_response = {
            "data": {
                "groups": {
                    "assignUser": {
                        "responseResult": {"succeeded": True}
                    }
                }
            }
        }
        endpoint._post = AsyncMock(return_value=mock_response)

        result = await endpoint.assign_user(group_id=1, user_id=5)

        assert result is True

    @pytest.mark.asyncio
    async def test_unassign_user(self, endpoint):
        """Test removing a user from a group."""
        mock_response = {
            "data": {
                "groups": {
                    "unassignUser": {
                        "responseResult": {"succeeded": True}
                    }
                }
            }
        }
        endpoint._post = AsyncMock(return_value=mock_response)

        result = await endpoint.unassign_user(group_id=1, user_id=5)

        assert result is True

    @pytest.mark.asyncio
    async def test_validation_errors(self, endpoint):
        """Test validation errors."""
        with pytest.raises(ValidationError):
            await endpoint.get(0)

        with pytest.raises(ValidationError):
            await endpoint.delete(-1)

        with pytest.raises(ValidationError):
            await endpoint.assign_user(0, 1)
