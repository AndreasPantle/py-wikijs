"""Groups endpoint for Wiki.js API."""

from typing import Dict, List, Union

from ..exceptions import APIError, ValidationError
from ..models import Group, GroupCreate, GroupUpdate
from .base import BaseEndpoint


class GroupsEndpoint(BaseEndpoint):
    """Endpoint for managing Wiki.js groups.

    Provides methods to:
    - List all groups
    - Get a specific group by ID
    - Create new groups
    - Update existing groups
    - Delete groups
    - Assign users to groups
    - Remove users from groups
    """

    def list(self) -> List[Group]:
        """List all groups.

        Returns:
            List of Group objects

        Raises:
            APIError: If the API request fails

        Example:
            >>> groups = client.groups.list()
            >>> for group in groups:
            ...     print(f"{group.name}: {len(group.users)} users")
        """
        query = """
        query {
            groups {
                list {
                    id
                    name
                    isSystem
                    redirectOnLogin
                    permissions
                    pageRules {
                        id
                        path
                        roles
                        match
                        deny
                        locales
                    }
                    users {
                        id
                        name
                        email
                    }
                    createdAt
                    updatedAt
                }
            }
        }
        """

        response = self._post("/graphql", json_data={"query": query})

        # Check for GraphQL errors
        if "errors" in response:
            raise APIError(f"GraphQL errors: {response['errors']}")

        # Extract and normalize groups
        groups_data = response.get("data", {}).get("groups", {}).get("list", [])
        return [Group(**self._normalize_group_data(g)) for g in groups_data]

    def get(self, group_id: int) -> Group:
        """Get a specific group by ID.

        Args:
            group_id: The group ID

        Returns:
            Group object with user list

        Raises:
            ValidationError: If group_id is invalid
            APIError: If the group is not found or API request fails

        Example:
            >>> group = client.groups.get(1)
            >>> print(f"{group.name}: {group.permissions}")
        """
        # Validate group_id
        if not isinstance(group_id, int) or group_id <= 0:
            raise ValidationError("group_id must be a positive integer")

        query = """
        query ($id: Int!) {
            groups {
                single(id: $id) {
                    id
                    name
                    isSystem
                    redirectOnLogin
                    permissions
                    pageRules {
                        id
                        path
                        roles
                        match
                        deny
                        locales
                    }
                    users {
                        id
                        name
                        email
                    }
                    createdAt
                    updatedAt
                }
            }
        }
        """

        response = self._post(
            "/graphql", json_data={"query": query, "variables": {"id": group_id}}
        )

        # Check for GraphQL errors
        if "errors" in response:
            raise APIError(f"GraphQL errors: {response['errors']}")

        # Extract group data
        group_data = response.get("data", {}).get("groups", {}).get("single")

        if not group_data:
            raise APIError(f"Group with ID {group_id} not found")

        return Group(**self._normalize_group_data(group_data))

    def create(self, group_data: Union[GroupCreate, Dict]) -> Group:
        """Create a new group.

        Args:
            group_data: GroupCreate object or dict with group data

        Returns:
            Created Group object

        Raises:
            ValidationError: If group data is invalid
            APIError: If the API request fails

        Example:
            >>> from wikijs.models import GroupCreate
            >>> group_data = GroupCreate(
            ...     name="Editors",
            ...     permissions=["read:pages", "write:pages"]
            ... )
            >>> group = client.groups.create(group_data)
        """
        # Validate and convert to dict
        if isinstance(group_data, dict):
            try:
                group_data = GroupCreate(**group_data)
            except Exception as e:
                raise ValidationError(f"Invalid group data: {e}")
        elif not isinstance(group_data, GroupCreate):
            raise ValidationError("group_data must be a GroupCreate object or dict")

        # Build mutation
        mutation = """
        mutation ($name: String!, $redirectOnLogin: String, $permissions: [String]!, $pageRules: [PageRuleInput]!) {
            groups {
                create(
                    name: $name
                    redirectOnLogin: $redirectOnLogin
                    permissions: $permissions
                    pageRules: $pageRules
                ) {
                    responseResult {
                        succeeded
                        errorCode
                        slug
                        message
                    }
                    group {
                        id
                        name
                        isSystem
                        redirectOnLogin
                        permissions
                        pageRules {
                            id
                            path
                            roles
                            match
                            deny
                            locales
                        }
                        createdAt
                        updatedAt
                    }
                }
            }
        }
        """

        variables = {
            "name": group_data.name,
            "redirectOnLogin": group_data.redirect_on_login or "/",
            "permissions": group_data.permissions,
            "pageRules": group_data.page_rules,
        }

        response = self._post(
            "/graphql", json_data={"query": mutation, "variables": variables}
        )

        # Check for GraphQL errors
        if "errors" in response:
            raise APIError(f"GraphQL errors: {response['errors']}")

        # Check response result
        result = response.get("data", {}).get("groups", {}).get("create", {})
        response_result = result.get("responseResult", {})

        if not response_result.get("succeeded"):
            error_msg = response_result.get("message", "Unknown error")
            raise APIError(f"Failed to create group: {error_msg}")

        # Extract and return created group
        group_data = result.get("group")
        if not group_data:
            raise APIError("Group created but no data returned")

        return Group(**self._normalize_group_data(group_data))

    def update(self, group_id: int, group_data: Union[GroupUpdate, Dict]) -> Group:
        """Update an existing group.

        Args:
            group_id: The group ID
            group_data: GroupUpdate object or dict with fields to update

        Returns:
            Updated Group object

        Raises:
            ValidationError: If group_id or group_data is invalid
            APIError: If the API request fails

        Example:
            >>> from wikijs.models import GroupUpdate
            >>> update_data = GroupUpdate(
            ...     name="Senior Editors",
            ...     permissions=["read:pages", "write:pages", "delete:pages"]
            ... )
            >>> group = client.groups.update(1, update_data)
        """
        # Validate group_id
        if not isinstance(group_id, int) or group_id <= 0:
            raise ValidationError("group_id must be a positive integer")

        # Validate and convert to dict
        if isinstance(group_data, dict):
            try:
                group_data = GroupUpdate(**group_data)
            except Exception as e:
                raise ValidationError(f"Invalid group data: {e}")
        elif not isinstance(group_data, GroupUpdate):
            raise ValidationError("group_data must be a GroupUpdate object or dict")

        # Build mutation with only non-None fields
        mutation = """
        mutation ($id: Int!, $name: String, $redirectOnLogin: String, $permissions: [String], $pageRules: [PageRuleInput]) {
            groups {
                update(
                    id: $id
                    name: $name
                    redirectOnLogin: $redirectOnLogin
                    permissions: $permissions
                    pageRules: $pageRules
                ) {
                    responseResult {
                        succeeded
                        errorCode
                        slug
                        message
                    }
                    group {
                        id
                        name
                        isSystem
                        redirectOnLogin
                        permissions
                        pageRules {
                            id
                            path
                            roles
                            match
                            deny
                            locales
                        }
                        createdAt
                        updatedAt
                    }
                }
            }
        }
        """

        variables = {"id": group_id}

        # Add only non-None fields to variables
        if group_data.name is not None:
            variables["name"] = group_data.name
        if group_data.redirect_on_login is not None:
            variables["redirectOnLogin"] = group_data.redirect_on_login
        if group_data.permissions is not None:
            variables["permissions"] = group_data.permissions
        if group_data.page_rules is not None:
            variables["pageRules"] = group_data.page_rules

        response = self._post(
            "/graphql", json_data={"query": mutation, "variables": variables}
        )

        # Check for GraphQL errors
        if "errors" in response:
            raise APIError(f"GraphQL errors: {response['errors']}")

        # Check response result
        result = response.get("data", {}).get("groups", {}).get("update", {})
        response_result = result.get("responseResult", {})

        if not response_result.get("succeeded"):
            error_msg = response_result.get("message", "Unknown error")
            raise APIError(f"Failed to update group: {error_msg}")

        # Extract and return updated group
        group_data_response = result.get("group")
        if not group_data_response:
            raise APIError("Group updated but no data returned")

        return Group(**self._normalize_group_data(group_data_response))

    def delete(self, group_id: int) -> bool:
        """Delete a group.

        Args:
            group_id: The group ID

        Returns:
            True if deletion was successful

        Raises:
            ValidationError: If group_id is invalid
            APIError: If the API request fails

        Example:
            >>> success = client.groups.delete(5)
            >>> if success:
            ...     print("Group deleted")
        """
        # Validate group_id
        if not isinstance(group_id, int) or group_id <= 0:
            raise ValidationError("group_id must be a positive integer")

        mutation = """
        mutation ($id: Int!) {
            groups {
                delete(id: $id) {
                    responseResult {
                        succeeded
                        errorCode
                        slug
                        message
                    }
                }
            }
        }
        """

        response = self._post(
            "/graphql", json_data={"query": mutation, "variables": {"id": group_id}}
        )

        # Check for GraphQL errors
        if "errors" in response:
            raise APIError(f"GraphQL errors: {response['errors']}")

        # Check response result
        result = response.get("data", {}).get("groups", {}).get("delete", {})
        response_result = result.get("responseResult", {})

        if not response_result.get("succeeded"):
            error_msg = response_result.get("message", "Unknown error")
            raise APIError(f"Failed to delete group: {error_msg}")

        return True

    def assign_user(self, group_id: int, user_id: int) -> bool:
        """Assign a user to a group.

        Args:
            group_id: The group ID
            user_id: The user ID

        Returns:
            True if assignment was successful

        Raises:
            ValidationError: If group_id or user_id is invalid
            APIError: If the API request fails

        Example:
            >>> success = client.groups.assign_user(group_id=1, user_id=5)
            >>> if success:
            ...     print("User assigned to group")
        """
        # Validate IDs
        if not isinstance(group_id, int) or group_id <= 0:
            raise ValidationError("group_id must be a positive integer")
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValidationError("user_id must be a positive integer")

        mutation = """
        mutation ($groupId: Int!, $userId: Int!) {
            groups {
                assignUser(groupId: $groupId, userId: $userId) {
                    responseResult {
                        succeeded
                        errorCode
                        slug
                        message
                    }
                }
            }
        }
        """

        response = self._post(
            "/graphql",
            json_data={
                "query": mutation,
                "variables": {"groupId": group_id, "userId": user_id},
            },
        )

        # Check for GraphQL errors
        if "errors" in response:
            raise APIError(f"GraphQL errors: {response['errors']}")

        # Check response result
        result = response.get("data", {}).get("groups", {}).get("assignUser", {})
        response_result = result.get("responseResult", {})

        if not response_result.get("succeeded"):
            error_msg = response_result.get("message", "Unknown error")
            raise APIError(f"Failed to assign user to group: {error_msg}")

        return True

    def unassign_user(self, group_id: int, user_id: int) -> bool:
        """Remove a user from a group.

        Args:
            group_id: The group ID
            user_id: The user ID

        Returns:
            True if removal was successful

        Raises:
            ValidationError: If group_id or user_id is invalid
            APIError: If the API request fails

        Example:
            >>> success = client.groups.unassign_user(group_id=1, user_id=5)
            >>> if success:
            ...     print("User removed from group")
        """
        # Validate IDs
        if not isinstance(group_id, int) or group_id <= 0:
            raise ValidationError("group_id must be a positive integer")
        if not isinstance(user_id, int) or user_id <= 0:
            raise ValidationError("user_id must be a positive integer")

        mutation = """
        mutation ($groupId: Int!, $userId: Int!) {
            groups {
                unassignUser(groupId: $groupId, userId: $userId) {
                    responseResult {
                        succeeded
                        errorCode
                        slug
                        message
                    }
                }
            }
        }
        """

        response = self._post(
            "/graphql",
            json_data={
                "query": mutation,
                "variables": {"groupId": group_id, "userId": user_id},
            },
        )

        # Check for GraphQL errors
        if "errors" in response:
            raise APIError(f"GraphQL errors: {response['errors']}")

        # Check response result
        result = response.get("data", {}).get("groups", {}).get("unassignUser", {})
        response_result = result.get("responseResult", {})

        if not response_result.get("succeeded"):
            error_msg = response_result.get("message", "Unknown error")
            raise APIError(f"Failed to remove user from group: {error_msg}")

        return True

    def _normalize_group_data(self, data: Dict) -> Dict:
        """Normalize group data from API response to Python naming convention.

        Args:
            data: Raw group data from API

        Returns:
            Normalized group data with snake_case field names
        """
        normalized = {
            "id": data.get("id"),
            "name": data.get("name"),
            "is_system": data.get("isSystem", False),
            "redirect_on_login": data.get("redirectOnLogin"),
            "permissions": data.get("permissions", []),
            "page_rules": data.get("pageRules", []),
            "users": data.get("users", []),
            "created_at": data.get("createdAt"),
            "updated_at": data.get("updatedAt"),
        }

        return normalized

    def iter_all(self):
        """Iterate over all groups.

        Note: Groups API returns all groups at once, so this is equivalent
        to iterating over list().

        Yields:
            Group objects one at a time

        Example:
            >>> for group in client.groups.iter_all():
            ...     print(f"{group.name}: {len(group.users)} users")
        """
        for group in self.list():
            yield group
