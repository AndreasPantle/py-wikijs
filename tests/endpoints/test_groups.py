"""Tests for Groups endpoint."""

from unittest.mock import Mock

import pytest

from wikijs.endpoints import GroupsEndpoint
from wikijs.exceptions import APIError, ValidationError
from wikijs.models import Group, GroupCreate, GroupUpdate


class TestGroupsEndpoint:
    """Test GroupsEndpoint class."""

    @pytest.fixture
    def client(self):
        """Create mock client."""
        mock_client = Mock()
        mock_client.base_url = "https://wiki.example.com"
        mock_client._request = Mock()
        return mock_client

    @pytest.fixture
    def endpoint(self, client):
        """Create GroupsEndpoint instance."""
        return GroupsEndpoint(client)

    def test_list_groups(self, endpoint):
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
        endpoint._post = Mock(return_value=mock_response)

        groups = endpoint.list()

        assert len(groups) == 1
        assert isinstance(groups[0], Group)
        assert groups[0].name == "Administrators"

    def test_get_group(self, endpoint):
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
        endpoint._post = Mock(return_value=mock_response)

        group = endpoint.get(1)

        assert isinstance(group, Group)
        assert group.id == 1
        assert len(group.users) == 1

    def test_create_group(self, endpoint):
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
        endpoint._post = Mock(return_value=mock_response)

        group = endpoint.create(group_data)

        assert isinstance(group, Group)
        assert group.name == "Editors"

    def test_update_group(self, endpoint):
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
        endpoint._post = Mock(return_value=mock_response)

        group = endpoint.update(1, update_data)

        assert group.name == "Senior Editors"

    def test_delete_group(self, endpoint):
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
        endpoint._post = Mock(return_value=mock_response)

        result = endpoint.delete(1)

        assert result is True

    def test_assign_user(self, endpoint):
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
        endpoint._post = Mock(return_value=mock_response)

        result = endpoint.assign_user(group_id=1, user_id=5)

        assert result is True

    def test_unassign_user(self, endpoint):
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
        endpoint._post = Mock(return_value=mock_response)

        result = endpoint.unassign_user(group_id=1, user_id=5)

        assert result is True

    def test_validation_errors(self, endpoint):
        """Test validation errors."""
        with pytest.raises(ValidationError):
            endpoint.get(0)

        with pytest.raises(ValidationError):
            endpoint.delete(-1)

        with pytest.raises(ValidationError):
            endpoint.assign_user(0, 1)
