"""Extended tests for Groups endpoint to improve coverage."""

from unittest.mock import Mock
import pytest

from wikijs.endpoints import GroupsEndpoint
from wikijs.exceptions import APIError, ValidationError
from wikijs.models import GroupCreate, GroupUpdate


class TestGroupsEndpointExtended:
    """Extended test suite for GroupsEndpoint."""

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

    def test_list_groups_api_error(self, endpoint):
        """Test list groups with API error."""
        mock_response = {"errors": [{"message": "API error"}]}
        endpoint._post = Mock(return_value=mock_response)

        with pytest.raises(APIError, match="API error"):
            endpoint.list()

    def test_get_group_not_found(self, endpoint):
        """Test get group when not found."""
        mock_response = {
            "data": {
                "groups": {
                    "single": None
                }
            }
        }
        endpoint._post = Mock(return_value=mock_response)

        with pytest.raises(APIError, match="not found"):
            endpoint.get(999)

    def test_get_group_api_error(self, endpoint):
        """Test get group with API error."""
        mock_response = {"errors": [{"message": "Access denied"}]}
        endpoint._post = Mock(return_value=mock_response)

        with pytest.raises(APIError, match="Access denied"):
            endpoint.get(1)

    def test_create_group_with_dict(self, endpoint):
        """Test creating group with dictionary."""
        group_dict = {"name": "Editors", "permissions": ["read:pages"]}

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

        group = endpoint.create(group_dict)
        assert group.name == "Editors"

    def test_create_group_validation_error(self, endpoint):
        """Test create group with validation error."""
        with pytest.raises(ValidationError):
            endpoint.create("invalid_type")

    def test_create_group_api_error(self, endpoint):
        """Test create group with API error."""
        group_data = GroupCreate(name="Editors")
        mock_response = {"errors": [{"message": "Group exists"}]}
        endpoint._post = Mock(return_value=mock_response)

        with pytest.raises(APIError, match="Group exists"):
            endpoint.create(group_data)

    def test_create_group_failed_result(self, endpoint):
        """Test create group with failed result."""
        group_data = GroupCreate(name="Editors")
        mock_response = {
            "data": {
                "groups": {
                    "create": {
                        "responseResult": {"succeeded": False, "message": "Creation failed"}
                    }
                }
            }
        }
        endpoint._post = Mock(return_value=mock_response)

        with pytest.raises(APIError, match="Creation failed"):
            endpoint.create(group_data)

    def test_update_group_validation_error_invalid_id(self, endpoint):
        """Test update group with invalid ID."""
        update_data = GroupUpdate(name="Updated")

        with pytest.raises(ValidationError):
            endpoint.update(0, update_data)

    def test_update_group_with_dict(self, endpoint):
        """Test updating group with dictionary."""
        update_dict = {"name": "Updated Name"}

        mock_response = {
            "data": {
                "groups": {
                    "update": {
                        "responseResult": {"succeeded": True},
                        "group": {
                            "id": 1,
                            "name": "Updated Name",
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

        group = endpoint.update(1, update_dict)
        assert group.name == "Updated Name"

    def test_update_group_validation_error_invalid_data(self, endpoint):
        """Test update group with invalid data."""
        with pytest.raises(ValidationError):
            endpoint.update(1, "invalid_type")

    def test_update_group_api_error(self, endpoint):
        """Test update group with API error."""
        update_data = GroupUpdate(name="Updated")
        mock_response = {"errors": [{"message": "Update failed"}]}
        endpoint._post = Mock(return_value=mock_response)

        with pytest.raises(APIError, match="Update failed"):
            endpoint.update(1, update_data)

    def test_update_group_failed_result(self, endpoint):
        """Test update group with failed result."""
        update_data = GroupUpdate(name="Updated")
        mock_response = {
            "data": {
                "groups": {
                    "update": {
                        "responseResult": {"succeeded": False, "message": "Update denied"}
                    }
                }
            }
        }
        endpoint._post = Mock(return_value=mock_response)

        with pytest.raises(APIError, match="Update denied"):
            endpoint.update(1, update_data)

    def test_delete_group_validation_error(self, endpoint):
        """Test delete group with invalid ID."""
        with pytest.raises(ValidationError):
            endpoint.delete(-1)

    def test_delete_group_api_error(self, endpoint):
        """Test delete group with API error."""
        mock_response = {"errors": [{"message": "Delete failed"}]}
        endpoint._post = Mock(return_value=mock_response)

        with pytest.raises(APIError, match="Delete failed"):
            endpoint.delete(1)

    def test_delete_group_failed_result(self, endpoint):
        """Test delete group with failed result."""
        mock_response = {
            "data": {
                "groups": {
                    "delete": {
                        "responseResult": {"succeeded": False, "message": "Cannot delete system group"}
                    }
                }
            }
        }
        endpoint._post = Mock(return_value=mock_response)

        with pytest.raises(APIError, match="Cannot delete system group"):
            endpoint.delete(1)

    def test_assign_user_validation_error_invalid_group(self, endpoint):
        """Test assign user with invalid group ID."""
        with pytest.raises(ValidationError):
            endpoint.assign_user(0, 1)

    def test_assign_user_validation_error_invalid_user(self, endpoint):
        """Test assign user with invalid user ID."""
        with pytest.raises(ValidationError):
            endpoint.assign_user(1, 0)

    def test_assign_user_api_error(self, endpoint):
        """Test assign user with API error."""
        mock_response = {"errors": [{"message": "Assignment failed"}]}
        endpoint._post = Mock(return_value=mock_response)

        with pytest.raises(APIError, match="Assignment failed"):
            endpoint.assign_user(1, 5)

    def test_assign_user_failed_result(self, endpoint):
        """Test assign user with failed result."""
        mock_response = {
            "data": {
                "groups": {
                    "assignUser": {
                        "responseResult": {"succeeded": False, "message": "User already in group"}
                    }
                }
            }
        }
        endpoint._post = Mock(return_value=mock_response)

        with pytest.raises(APIError, match="User already in group"):
            endpoint.assign_user(1, 5)

    def test_unassign_user_validation_error_invalid_group(self, endpoint):
        """Test unassign user with invalid group ID."""
        with pytest.raises(ValidationError):
            endpoint.unassign_user(-1, 1)

    def test_unassign_user_validation_error_invalid_user(self, endpoint):
        """Test unassign user with invalid user ID."""
        with pytest.raises(ValidationError):
            endpoint.unassign_user(1, -1)

    def test_unassign_user_api_error(self, endpoint):
        """Test unassign user with API error."""
        mock_response = {"errors": [{"message": "Unassignment failed"}]}
        endpoint._post = Mock(return_value=mock_response)

        with pytest.raises(APIError, match="Unassignment failed"):
            endpoint.unassign_user(1, 5)

    def test_unassign_user_failed_result(self, endpoint):
        """Test unassign user with failed result."""
        mock_response = {
            "data": {
                "groups": {
                    "unassignUser": {
                        "responseResult": {"succeeded": False, "message": "User not in group"}
                    }
                }
            }
        }
        endpoint._post = Mock(return_value=mock_response)

        with pytest.raises(APIError, match="User not in group"):
            endpoint.unassign_user(1, 5)
