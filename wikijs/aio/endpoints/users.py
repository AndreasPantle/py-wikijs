"""Async Users API endpoint for wikijs-python-sdk."""

from typing import Any, Dict, List, Optional, Union

from ...exceptions import APIError, ValidationError
from ...models.user import User, UserCreate, UserUpdate
from .base import AsyncBaseEndpoint


class AsyncUsersEndpoint(AsyncBaseEndpoint):
    """Async endpoint for Wiki.js Users API operations.

    This endpoint provides async methods for creating, reading, updating, and
    deleting users through the Wiki.js GraphQL API.

    Example:
        >>> async with AsyncWikiJSClient('https://wiki.example.com', auth='key') as client:
        ...     users = client.users
        ...
        ...     # List all users
        ...     all_users = await users.list()
        ...
        ...     # Get a specific user
        ...     user = await users.get(123)
        ...
        ...     # Create a new user
        ...     new_user_data = UserCreate(
        ...         email="user@example.com",
        ...         name="John Doe",
        ...         password_raw="secure_password"
        ...     )
        ...     created_user = await users.create(new_user_data)
        ...
        ...     # Update an existing user
        ...     update_data = UserUpdate(name="Jane Doe")
        ...     updated_user = await users.update(123, update_data)
        ...
        ...     # Delete a user
        ...     await users.delete(123)
    """

    async def list(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        search: Optional[str] = None,
        order_by: str = "name",
        order_direction: str = "ASC",
    ) -> List[User]:
        """List users with optional filtering.

        Args:
            limit: Maximum number of users to return
            offset: Number of users to skip
            search: Search term to filter users
            order_by: Field to order by (name, email, createdAt)
            order_direction: Order direction (ASC or DESC)

        Returns:
            List of User objects

        Raises:
            APIError: If the API request fails
            ValidationError: If parameters are invalid
        """
        # Validate parameters
        if limit is not None and limit < 1:
            raise ValidationError("limit must be greater than 0")

        if offset is not None and offset < 0:
            raise ValidationError("offset must be non-negative")

        if order_by not in ["name", "email", "createdAt", "lastLoginAt"]:
            raise ValidationError(
                "order_by must be one of: name, email, createdAt, lastLoginAt"
            )

        if order_direction not in ["ASC", "DESC"]:
            raise ValidationError("order_direction must be ASC or DESC")

        # Build GraphQL query
        query = """
        query($filter: String, $orderBy: String) {
            users {
                list(filter: $filter, orderBy: $orderBy) {
                    id
                    name
                    email
                    providerKey
                    isSystem
                    isActive
                    isVerified
                    location
                    jobTitle
                    timezone
                    createdAt
                    updatedAt
                    lastLoginAt
                }
            }
        }
        """

        # Build variables
        variables: Dict[str, Any] = {}
        if search:
            variables["filter"] = search
        if order_by:
            # Wiki.js expects format like "name ASC"
            variables["orderBy"] = f"{order_by} {order_direction}"

        # Make request
        response = await self._post(
            "/graphql",
            json_data=(
                {"query": query, "variables": variables}
                if variables
                else {"query": query}
            ),
        )

        # Parse response
        if "errors" in response:
            raise APIError(f"GraphQL errors: {response['errors']}")

        users_data = response.get("data", {}).get("users", {}).get("list", [])

        # Apply client-side pagination if needed
        if offset:
            users_data = users_data[offset:]
        if limit:
            users_data = users_data[:limit]

        # Convert to User objects
        users = []
        for user_data in users_data:
            try:
                normalized_data = self._normalize_user_data(user_data)
                user = User(**normalized_data)
                users.append(user)
            except Exception as e:
                raise APIError(f"Failed to parse user data: {str(e)}") from e

        return users

    async def get(self, user_id: int) -> User:
        """Get a specific user by ID.

        Args:
            user_id: The user ID

        Returns:
            User object

        Raises:
            APIError: If the user is not found or request fails
            ValidationError: If user_id is invalid
        """
        if not isinstance(user_id, int) or user_id < 1:
            raise ValidationError("user_id must be a positive integer")

        # Build GraphQL query
        query = """
        query($id: Int!) {
            users {
                single(id: $id) {
                    id
                    name
                    email
                    providerKey
                    isSystem
                    isActive
                    isVerified
                    location
                    jobTitle
                    timezone
                    groups {
                        id
                        name
                    }
                    createdAt
                    updatedAt
                    lastLoginAt
                }
            }
        }
        """

        # Make request
        response = await self._post(
            "/graphql",
            json_data={"query": query, "variables": {"id": user_id}},
        )

        # Parse response
        if "errors" in response:
            raise APIError(f"GraphQL errors: {response['errors']}")

        user_data = response.get("data", {}).get("users", {}).get("single")
        if not user_data:
            raise APIError(f"User with ID {user_id} not found")

        # Convert to User object
        try:
            normalized_data = self._normalize_user_data(user_data)
            return User(**normalized_data)
        except Exception as e:
            raise APIError(f"Failed to parse user data: {str(e)}") from e

    async def create(self, user_data: Union[UserCreate, Dict[str, Any]]) -> User:
        """Create a new user.

        Args:
            user_data: User creation data (UserCreate object or dict)

        Returns:
            Created User object

        Raises:
            APIError: If user creation fails
            ValidationError: If user data is invalid
        """
        # Convert to UserCreate if needed
        if isinstance(user_data, dict):
            try:
                user_data = UserCreate(**user_data)
            except Exception as e:
                raise ValidationError(f"Invalid user data: {str(e)}") from e
        elif not isinstance(user_data, UserCreate):
            raise ValidationError("user_data must be UserCreate object or dict")

        # Build GraphQL mutation
        mutation = """
        mutation(
            $email: String!,
            $name: String!,
            $passwordRaw: String!,
            $providerKey: String!,
            $groups: [Int]!,
            $mustChangePassword: Boolean!,
            $sendWelcomeEmail: Boolean!,
            $location: String,
            $jobTitle: String,
            $timezone: String
        ) {
            users {
                create(
                    email: $email,
                    name: $name,
                    passwordRaw: $passwordRaw,
                    providerKey: $providerKey,
                    groups: $groups,
                    mustChangePassword: $mustChangePassword,
                    sendWelcomeEmail: $sendWelcomeEmail,
                    location: $location,
                    jobTitle: $jobTitle,
                    timezone: $timezone
                ) {
                    responseResult {
                        succeeded
                        errorCode
                        slug
                        message
                    }
                    user {
                        id
                        name
                        email
                        providerKey
                        isSystem
                        isActive
                        isVerified
                        location
                        jobTitle
                        timezone
                        createdAt
                        updatedAt
                    }
                }
            }
        }
        """

        # Build variables
        variables = {
            "email": user_data.email,
            "name": user_data.name,
            "passwordRaw": user_data.password_raw,
            "providerKey": user_data.provider_key,
            "groups": user_data.groups,
            "mustChangePassword": user_data.must_change_password,
            "sendWelcomeEmail": user_data.send_welcome_email,
            "location": user_data.location,
            "jobTitle": user_data.job_title,
            "timezone": user_data.timezone,
        }

        # Make request
        response = await self._post(
            "/graphql", json_data={"query": mutation, "variables": variables}
        )

        # Parse response
        if "errors" in response:
            raise APIError(f"Failed to create user: {response['errors']}")

        create_result = response.get("data", {}).get("users", {}).get("create", {})
        response_result = create_result.get("responseResult", {})

        if not response_result.get("succeeded"):
            error_msg = response_result.get("message", "Unknown error")
            raise APIError(f"User creation failed: {error_msg}")

        created_user_data = create_result.get("user")
        if not created_user_data:
            raise APIError("User creation failed - no user data returned")

        # Convert to User object
        try:
            normalized_data = self._normalize_user_data(created_user_data)
            return User(**normalized_data)
        except Exception as e:
            raise APIError(f"Failed to parse created user data: {str(e)}") from e

    async def update(
        self, user_id: int, user_data: Union[UserUpdate, Dict[str, Any]]
    ) -> User:
        """Update an existing user.

        Args:
            user_id: The user ID
            user_data: User update data (UserUpdate object or dict)

        Returns:
            Updated User object

        Raises:
            APIError: If user update fails
            ValidationError: If parameters are invalid
        """
        if not isinstance(user_id, int) or user_id < 1:
            raise ValidationError("user_id must be a positive integer")

        # Convert to UserUpdate if needed
        if isinstance(user_data, dict):
            try:
                user_data = UserUpdate(**user_data)
            except Exception as e:
                raise ValidationError(f"Invalid user data: {str(e)}") from e
        elif not isinstance(user_data, UserUpdate):
            raise ValidationError("user_data must be UserUpdate object or dict")

        # Build GraphQL mutation
        mutation = """
        mutation(
            $id: Int!,
            $email: String,
            $name: String,
            $passwordRaw: String,
            $location: String,
            $jobTitle: String,
            $timezone: String,
            $groups: [Int],
            $isActive: Boolean,
            $isVerified: Boolean
        ) {
            users {
                update(
                    id: $id,
                    email: $email,
                    name: $name,
                    passwordRaw: $passwordRaw,
                    location: $location,
                    jobTitle: $jobTitle,
                    timezone: $timezone,
                    groups: $groups,
                    isActive: $isActive,
                    isVerified: $isVerified
                ) {
                    responseResult {
                        succeeded
                        errorCode
                        slug
                        message
                    }
                    user {
                        id
                        name
                        email
                        providerKey
                        isSystem
                        isActive
                        isVerified
                        location
                        jobTitle
                        timezone
                        createdAt
                        updatedAt
                    }
                }
            }
        }
        """

        # Build variables (only include non-None values)
        variables: Dict[str, Any] = {"id": user_id}

        if user_data.name is not None:
            variables["name"] = user_data.name
        if user_data.email is not None:
            variables["email"] = str(user_data.email)
        if user_data.password_raw is not None:
            variables["passwordRaw"] = user_data.password_raw
        if user_data.location is not None:
            variables["location"] = user_data.location
        if user_data.job_title is not None:
            variables["jobTitle"] = user_data.job_title
        if user_data.timezone is not None:
            variables["timezone"] = user_data.timezone
        if user_data.groups is not None:
            variables["groups"] = user_data.groups
        if user_data.is_active is not None:
            variables["isActive"] = user_data.is_active
        if user_data.is_verified is not None:
            variables["isVerified"] = user_data.is_verified

        # Make request
        response = await self._post(
            "/graphql", json_data={"query": mutation, "variables": variables}
        )

        # Parse response
        if "errors" in response:
            raise APIError(f"Failed to update user: {response['errors']}")

        update_result = response.get("data", {}).get("users", {}).get("update", {})
        response_result = update_result.get("responseResult", {})

        if not response_result.get("succeeded"):
            error_msg = response_result.get("message", "Unknown error")
            raise APIError(f"User update failed: {error_msg}")

        updated_user_data = update_result.get("user")
        if not updated_user_data:
            raise APIError("User update failed - no user data returned")

        # Convert to User object
        try:
            normalized_data = self._normalize_user_data(updated_user_data)
            return User(**normalized_data)
        except Exception as e:
            raise APIError(f"Failed to parse updated user data: {str(e)}") from e

    async def delete(self, user_id: int) -> bool:
        """Delete a user.

        Args:
            user_id: The user ID

        Returns:
            True if deletion was successful

        Raises:
            APIError: If user deletion fails
            ValidationError: If user_id is invalid
        """
        if not isinstance(user_id, int) or user_id < 1:
            raise ValidationError("user_id must be a positive integer")

        # Build GraphQL mutation
        mutation = """
        mutation($id: Int!) {
            users {
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

        # Make request
        response = await self._post(
            "/graphql",
            json_data={"query": mutation, "variables": {"id": user_id}},
        )

        # Parse response
        if "errors" in response:
            raise APIError(f"Failed to delete user: {response['errors']}")

        delete_result = response.get("data", {}).get("users", {}).get("delete", {})
        response_result = delete_result.get("responseResult", {})

        if not response_result.get("succeeded"):
            error_msg = response_result.get("message", "Unknown error")
            raise APIError(f"User deletion failed: {error_msg}")

        return True

    async def search(self, query: str, limit: Optional[int] = None) -> List[User]:
        """Search for users by name or email.

        Args:
            query: Search query string
            limit: Maximum number of results to return

        Returns:
            List of matching User objects

        Raises:
            APIError: If search fails
            ValidationError: If parameters are invalid
        """
        if not query or not isinstance(query, str):
            raise ValidationError("query must be a non-empty string")

        if limit is not None and limit < 1:
            raise ValidationError("limit must be greater than 0")

        # Use the list method with search parameter
        return await self.list(search=query, limit=limit)

    def _normalize_user_data(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize user data from API response to model format.

        Args:
            user_data: Raw user data from API

        Returns:
            Normalized data for User model
        """
        normalized = {}

        # Map API field names to model field names
        field_mapping = {
            "id": "id",
            "name": "name",
            "email": "email",
            "providerKey": "provider_key",
            "isSystem": "is_system",
            "isActive": "is_active",
            "isVerified": "is_verified",
            "location": "location",
            "jobTitle": "job_title",
            "timezone": "timezone",
            "createdAt": "created_at",
            "updatedAt": "updated_at",
            "lastLoginAt": "last_login_at",
        }

        for api_field, model_field in field_mapping.items():
            if api_field in user_data:
                normalized[model_field] = user_data[api_field]

        # Handle groups - convert from API format
        if "groups" in user_data:
            if isinstance(user_data["groups"], list):
                # Convert each group dict to proper format
                normalized["groups"] = [
                    {"id": g["id"], "name": g["name"]}
                    for g in user_data["groups"]
                    if isinstance(g, dict)
                ]
            else:
                normalized["groups"] = []
        else:
            normalized["groups"] = []

        return normalized

    async def iter_all(
        self,
        batch_size: int = 50,
        search: Optional[str] = None,
        order_by: str = "name",
        order_direction: str = "ASC",
    ):
        """Iterate over all users asynchronously with automatic pagination.

        Args:
            batch_size: Number of users to fetch per request (default: 50)
            search: Search term to filter users
            order_by: Field to sort by
            order_direction: Sort direction (ASC or DESC)

        Yields:
            User objects one at a time

        Example:
            >>> async for user in client.users.iter_all():
            ...     print(f"{user.name} ({user.email})")
        """
        offset = 0
        while True:
            batch = await self.list(
                limit=batch_size,
                offset=offset,
                search=search,
                order_by=order_by,
                order_direction=order_direction,
            )

            if not batch:
                break

            for user in batch:
                yield user

            if len(batch) < batch_size:
                break

            offset += batch_size
