"""Pages API endpoint for py-wikijs."""

from typing import Any, Dict, List, Optional, Union

from ..cache import CacheKey
from ..exceptions import APIError, ValidationError
from ..models.page import Page, PageCreate, PageUpdate
from .base import BaseEndpoint


class PagesEndpoint(BaseEndpoint):
    """Endpoint for Wiki.js Pages API operations.

    This endpoint provides methods for creating, reading, updating, and deleting
    wiki pages through the Wiki.js GraphQL API.

    Example:
        >>> client = WikiJSClient('https://wiki.example.com', auth='api-key')
        >>> pages = client.pages
        >>>
        >>> # List all pages
        >>> all_pages = pages.list()
        >>>
        >>> # Get a specific page
        >>> page = pages.get(123)
        >>>
        >>> # Create a new page
        >>> new_page_data = PageCreate(
        ...     title="Getting Started",
        ...     path="getting-started",
        ...     content="# Welcome\\n\\nThis is your first page!"
        ... )
        >>> created_page = pages.create(new_page_data)
        >>>
        >>> # Update an existing page
        >>> update_data = PageUpdate(title="Updated Title")
        >>> updated_page = pages.update(123, update_data)
        >>>
        >>> # Delete a page
        >>> pages.delete(123)
    """

    def list(
        self,
        limit: Optional[int] = None,
        orderby: str = "TITLE",
        orderbydirection: str = "ASC",
        tags: Optional[List[str]] = None,
        locale: Optional[str] = None,
        creatorid: Optional[int] = None,
        authorid: Optional[int] = None,
    ) -> List[Page]:
        """List pages with optional filtering.

        Args:
            limit: Maximum number of pages to return
            orderby: Field to order by (CREATED, ID, PATH, TITLE, UPDATED)
            orderbydirection: Order direction (ASC or DESC)
            tags: List of tags to filter by (pages must have ALL tags)
            locale: Locale to filter by
            creatorid: Creator ID to filter by
            authorid: Author ID to filter by

        Returns:
            List of Page objects

        Raises:
            APIError: If the API request fails
            ValidationError: If parameters are invalid
        """
        # Validate parameters
        if limit is not None and limit < 1:
            raise ValidationError("limit must be greater than 0")

        if orderby not in ["CREATED", "ID", "PATH", "TITLE", "UPDATED"]:
            raise ValidationError(
                "orderby must be one of: CREATED, ID, PATH, TITLE, UPDATED"
            )

        if orderbydirection not in ["ASC", "DESC"]:
            raise ValidationError("orderbydirection must be ASC or DESC")

        # Build GraphQL query with variables using actual Wiki.js schema
        query = """
        query($limit: Int, $orderBy: PageOrderBy, $orderByDirection: PageOrderByDirection, $tags: [String!], $locale: String, $creatorId: Int, $authorId: Int) {
            pages {
                list(limit: $limit, orderBy: $orderBy, orderByDirection: $orderByDirection, tags: $tags, locale: $locale, creatorId: $creatorId, authorId: $authorId) {
                    id
                    path
                    locale
                    title
                    description
                    contentType
                    isPublished
                    isPrivate
                    privateNS
                    createdAt
                    updatedAt
                    tags
                }
            }
        }
        """

        # Build variables object
        variables: Dict[str, Any] = {}
        if limit is not None:
            variables["limit"] = limit
        if tags is not None:
            variables["tags"] = tags
        if locale is not None:
            variables["locale"] = locale
        if creatorid is not None:
            variables["creatorId"] = creatorid
        if authorid is not None:
            variables["authorId"] = authorid
        if orderby is not None:
            variables["orderBy"] = orderby
        if orderbydirection is not None:
            variables["orderByDirection"] = orderbydirection

        # Make request with query and variables
        json_data: Dict[str, Any] = {"query": query}
        if variables:
            json_data["variables"] = variables

        response = self._post("/graphql", json_data=json_data)

        # Parse response
        if "errors" in response:
            raise APIError(f"GraphQL errors: {response['errors']}")

        pages_data = response.get("data", {}).get("pages", {}).get("list", [])

        # Convert to Page objects
        pages = []
        for page_data in pages_data:
            try:
                # Convert API field names to model field names
                normalized_data = self._normalize_page_data(page_data)
                page = Page(**normalized_data)
                pages.append(page)
            except Exception as e:
                raise APIError(f"Failed to parse page data: {str(e)}") from e

        return pages

    def get(self, page_id: int) -> Page:
        """Get a specific page by ID.

        Args:
            page_id: The page ID

        Returns:
            Page object

        Raises:
            APIError: If the page is not found or request fails
            ValidationError: If page_id is invalid
        """
        if not isinstance(page_id, int) or page_id < 1:
            raise ValidationError("page_id must be a positive integer")

        # Check cache if enabled
        if self._client.cache:
            cache_key = CacheKey("page", str(page_id), "get")
            cached = self._client.cache.get(cache_key)
            if cached is not None:
                return cached

        # Build GraphQL query using actual Wiki.js schema
        query = """
        query($id: Int!) {
            pages {
                single(id: $id) {
                    id
                    title
                    path
                    content
                    description
                    isPublished
                    isPrivate
                    tags {
                        tag
                    }
                    locale
                    authorId
                    authorName
                    authorEmail
                    editor
                    createdAt
                    updatedAt
                }
            }
        }
        """

        # Make request
        response = self._post(
            "/graphql",
            json_data={"query": query, "variables": {"id": page_id}},
        )

        # Parse response
        if "errors" in response:
            raise APIError(f"GraphQL errors: {response['errors']}")

        page_data = response.get("data", {}).get("pages", {}).get("single")
        if not page_data:
            raise APIError(f"Page with ID {page_id} not found")

        # Convert to Page object
        try:
            normalized_data = self._normalize_page_data(page_data)
            page = Page(**normalized_data)

            # Cache the result if cache is enabled
            if self._client.cache:
                cache_key = CacheKey("page", str(page_id), "get")
                self._client.cache.set(cache_key, page)

            return page
        except Exception as e:
            raise APIError(f"Failed to parse page data: {str(e)}") from e

    def get_by_path(self, path: str, locale: str = "en") -> Page:
        """Get a page by its path.

        Args:
            path: The page path (e.g., "getting-started")
            locale: The page locale (default: "en")

        Returns:
            Page object

        Raises:
            APIError: If the page is not found or request fails
            ValidationError: If path is invalid
        """
        if not path or not isinstance(path, str):
            raise ValidationError("path must be a non-empty string")

        # Normalize path
        path = path.strip("/")

        # Build GraphQL query
        query = """
        query($path: String!, $locale: String!) {
            pageByPath(path: $path, locale: $locale) {
                id
                title
                path
                content
                description
                isPublished
                isPrivate
                tags
                locale
                authorId
                authorName
                authorEmail
                editor
                createdAt
                updatedAt
            }
        }
        """

        # Make request
        response = self._post(
            "/graphql",
            json_data={
                "query": query,
                "variables": {"path": path, "locale": locale},
            },
        )

        # Parse response
        if "errors" in response:
            raise APIError(f"GraphQL errors: {response['errors']}")

        page_data = response.get("data", {}).get("pageByPath")
        if not page_data:
            raise APIError(f"Page with path '{path}' not found")

        # Convert to Page object
        try:
            normalized_data = self._normalize_page_data(page_data)
            return Page(**normalized_data)
        except Exception as e:
            raise APIError(f"Failed to parse page data: {str(e)}") from e

    def create(self, page_data: Union[PageCreate, Dict[str, Any]]) -> Page:
        """Create a new page.

        Args:
            page_data: Page creation data (PageCreate object or dict)

        Returns:
            Created Page object

        Raises:
            APIError: If page creation fails
            ValidationError: If page data is invalid
        """
        # Convert to PageCreate if needed
        if isinstance(page_data, dict):
            try:
                page_data = PageCreate(**page_data)
            except Exception as e:
                raise ValidationError(f"Invalid page data: {str(e)}") from e
        elif not isinstance(page_data, PageCreate):
            raise ValidationError("page_data must be PageCreate object or dict")

        # Build GraphQL mutation using actual Wiki.js schema
        mutation = """
        mutation(
            $content: String!,
            $description: String!,
            $editor: String!,
            $isPublished: Boolean!,
            $isPrivate: Boolean!,
            $locale: String!,
            $path: String!,
            $tags: [String]!,
            $title: String!
        ) {
            pages {
                create(
                    content: $content,
                    description: $description,
                    editor: $editor,
                    isPublished: $isPublished,
                    isPrivate: $isPrivate,
                    locale: $locale,
                    path: $path,
                    tags: $tags,
                    title: $title
                ) {
                    responseResult {
                        succeeded
                        errorCode
                        slug
                        message
                    }
                    page {
                        id
                        title
                        path
                        content
                        description
                        isPublished
                        isPrivate
                        tags {
                            tag
                        }
                        locale
                        authorId
                        authorName
                        authorEmail
                        editor
                        createdAt
                        updatedAt
                    }
                }
            }
        }
        """

        # Build variables from page data
        variables = {
            "title": page_data.title,
            "path": page_data.path,
            "content": page_data.content,
            "description": page_data.description
            or f"Created via SDK: {page_data.title}",
            "isPublished": page_data.is_published,
            "isPrivate": page_data.is_private,
            "tags": page_data.tags,
            "locale": page_data.locale,
            "editor": page_data.editor,
        }

        # Make request
        response = self._post(
            "/graphql", json_data={"query": mutation, "variables": variables}
        )

        # Parse response
        if "errors" in response:
            raise APIError(f"Failed to create page: {response['errors']}")

        create_result = response.get("data", {}).get("pages", {}).get("create", {})
        response_result = create_result.get("responseResult", {})

        if not response_result.get("succeeded"):
            error_msg = response_result.get("message", "Unknown error")
            raise APIError(f"Page creation failed: {error_msg}")

        created_page_data = create_result.get("page")
        if not created_page_data:
            raise APIError("Page creation failed - no page data returned")

        # Convert to Page object
        try:
            normalized_data = self._normalize_page_data(created_page_data)
            return Page(**normalized_data)
        except Exception as e:
            raise APIError(f"Failed to parse created page data: {str(e)}") from e

    def update(
        self, page_id: int, page_data: Union[PageUpdate, Dict[str, Any]]
    ) -> Page:
        """Update an existing page.

        Args:
            page_id: The page ID
            page_data: Page update data (PageUpdate object or dict)

        Returns:
            Updated Page object

        Raises:
            APIError: If page update fails
            ValidationError: If parameters are invalid
        """
        if not isinstance(page_id, int) or page_id < 1:
            raise ValidationError("page_id must be a positive integer")

        # Convert to PageUpdate if needed
        if isinstance(page_data, dict):
            try:
                page_data = PageUpdate(**page_data)
            except Exception as e:
                raise ValidationError(f"Invalid page data: {str(e)}") from e
        elif not isinstance(page_data, PageUpdate):
            raise ValidationError("page_data must be PageUpdate object or dict")

        # Build GraphQL mutation
        mutation = """
        mutation(
            $id: Int!,
            $title: String,
            $content: String,
            $description: String,
            $isPublished: Boolean,
            $isPrivate: Boolean,
            $tags: [String]
        ) {
            updatePage(
                id: $id,
                title: $title,
                content: $content,
                description: $description,
                isPublished: $isPublished,
                isPrivate: $isPrivate,
                tags: $tags
            ) {
                id
                title
                path
                content
                description
                isPublished
                isPrivate
                tags
                locale
                authorId
                authorName
                authorEmail
                editor
                createdAt
                updatedAt
            }
        }
        """

        # Build variables (only include non-None values)
        variables: Dict[str, Any] = {"id": page_id}

        if page_data.title is not None:
            variables["title"] = page_data.title
        if page_data.content is not None:
            variables["content"] = page_data.content
        if page_data.description is not None:
            variables["description"] = page_data.description
        if page_data.is_published is not None:
            variables["isPublished"] = page_data.is_published
        if page_data.is_private is not None:
            variables["isPrivate"] = page_data.is_private
        if page_data.tags is not None:
            variables["tags"] = page_data.tags

        # Make request
        response = self._post(
            "/graphql", json_data={"query": mutation, "variables": variables}
        )

        # Parse response
        if "errors" in response:
            raise APIError(f"Failed to update page: {response['errors']}")

        updated_page_data = response.get("data", {}).get("updatePage")
        if not updated_page_data:
            raise APIError("Page update failed - no data returned")

        # Invalidate cache for this page
        if self._client.cache:
            self._client.cache.invalidate_resource("page", str(page_id))

        # Convert to Page object
        try:
            normalized_data = self._normalize_page_data(updated_page_data)
            return Page(**normalized_data)
        except Exception as e:
            raise APIError(f"Failed to parse updated page data: {str(e)}") from e

    def delete(self, page_id: int) -> bool:
        """Delete a page.

        Args:
            page_id: The page ID

        Returns:
            True if deletion was successful

        Raises:
            APIError: If page deletion fails
            ValidationError: If page_id is invalid
        """
        if not isinstance(page_id, int) or page_id < 1:
            raise ValidationError("page_id must be a positive integer")

        # Build GraphQL mutation
        mutation = """
        mutation($id: Int!) {
            deletePage(id: $id) {
                success
                message
            }
        }
        """

        # Make request
        response = self._post(
            "/graphql",
            json_data={"query": mutation, "variables": {"id": page_id}},
        )

        # Parse response
        if "errors" in response:
            raise APIError(f"Failed to delete page: {response['errors']}")

        delete_result = response.get("data", {}).get("deletePage", {})
        success = delete_result.get("success", False)

        if not success:
            message = delete_result.get("message", "Unknown error")
            raise APIError(f"Page deletion failed: {message}")

        # Invalidate cache for this page
        if self._client.cache:
            self._client.cache.invalidate_resource("page", str(page_id))

        return True

    def search(
        self,
        query: str,
        limit: Optional[int] = None,
        locale: Optional[str] = None,
    ) -> List[Page]:
        """Search for pages by content and title.

        Args:
            query: Search query string
            limit: Maximum number of results to return
            locale: Locale to search in

        Returns:
            List of matching Page objects

        Raises:
            APIError: If search fails
            ValidationError: If parameters are invalid
        """
        if not query or not isinstance(query, str):
            raise ValidationError("query must be a non-empty string")

        if limit is not None and limit < 1:
            raise ValidationError("limit must be greater than 0")

        # Use the list method with search parameter
        return self.list(search=query, limit=limit, locale=locale)

    def get_by_tags(
        self,
        tags: List[str],
        match_all: bool = True,
        limit: Optional[int] = None,
    ) -> List[Page]:
        """Get pages by tags.

        Args:
            tags: List of tags to search for
            match_all: If True, pages must have ALL tags. If False, ANY tag matches
            limit: Maximum number of results to return

        Returns:
            List of matching Page objects

        Raises:
            APIError: If request fails
            ValidationError: If parameters are invalid
        """
        if not tags or not isinstance(tags, list):
            raise ValidationError("tags must be a non-empty list")

        if limit is not None and limit < 1:
            raise ValidationError("limit must be greater than 0")

        # For match_all=True, use the tags parameter directly
        if match_all:
            return self.list(tags=tags, limit=limit)

        # For match_all=False, we need a more complex query
        # This would require a custom GraphQL query or multiple requests
        # For now, implement a simple approach
        all_pages = self.list(
            limit=limit * 2 if limit else None
        )  # Get more pages to filter

        matching_pages = []
        for page in all_pages:
            if any(tag.lower() in [t.lower() for t in page.tags] for tag in tags):
                matching_pages.append(page)
                if limit and len(matching_pages) >= limit:
                    break

        return matching_pages

    def _normalize_page_data(self, page_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize page data from API response to model format.

        Args:
            page_data: Raw page data from API

        Returns:
            Normalized data for Page model
        """
        normalized = {}

        # Map API field names to model field names
        field_mapping = {
            "id": "id",
            "path": "path",
            "locale": "locale",
            "title": "title",
            "description": "description",
            "contentType": "content_type",
            "isPublished": "is_published",
            "isPrivate": "is_private",
            "privateNS": "private_ns",
            "createdAt": "created_at",
            "updatedAt": "updated_at",
            "content": "content",
            "tags": "tags",
            "authorId": "author_id",
            "authorName": "author_name",
            "authorEmail": "author_email",
            "editor": "editor"
        }

        for api_field, model_field in field_mapping.items():
            if api_field in page_data:
                normalized[model_field] = page_data[api_field]

        # Handle tags - convert from Wiki.js format
        if "tags" in page_data:
            if isinstance(page_data["tags"], list):
                # Handle both formats: ["tag1", "tag2"] or [{"tag": "tag1"}]
                tags = []
                for tag in page_data["tags"]:
                    if isinstance(tag, dict) and "tag" in tag:
                        tags.append(tag["tag"])
                    elif isinstance(tag, str):
                        tags.append(tag)
                normalized["tags"] = tags
            else:
                normalized["tags"] = []
        else:
            normalized["tags"] = []

        return normalized

    def iter_all(
        self,
        batch_size: int = 50,
        search: Optional[str] = None,
        tags: Optional[List[str]] = None,
        locale: Optional[str] = None,
        author_id: Optional[int] = None,
        order_by: str = "title",
        order_direction: str = "ASC",
    ):
        """Iterate over all pages with automatic pagination.

        This method automatically handles pagination, fetching pages in batches
        and yielding them one at a time.

        Args:
            batch_size: Number of pages to fetch per request (default: 50)
            search: Search term to filter pages
            tags: Filter by tags
            locale: Filter by locale
            author_id: Filter by author ID
            order_by: Field to sort by
            order_direction: Sort direction (ASC or DESC)

        Yields:
            Page objects one at a time

        Example:
            >>> for page in client.pages.iter_all():
            ...     print(f"{page.title}: {page.path}")
            >>>
            >>> # With filtering
            >>> for page in client.pages.iter_all(search="api", batch_size=100):
            ...     print(page.title)
        """
        offset = 0
        while True:
            batch = self.list(
                limit=batch_size,
                offset=offset,
                search=search,
                tags=tags,
                locale=locale,
                author_id=author_id,
                order_by=order_by,
                order_direction=order_direction,
            )

            if not batch:
                break

            for page in batch:
                yield page

            if len(batch) < batch_size:
                break

            offset += batch_size

    def create_many(
        self, pages_data: List[Union[PageCreate, Dict[str, Any]]]
    ) -> List[Page]:
        """Create multiple pages in a single batch operation.

        This method creates multiple pages efficiently by batching the operations.
        It's faster than calling create() multiple times.

        Args:
            pages_data: List of PageCreate objects or dicts

        Returns:
            List of created Page objects

        Raises:
            APIError: If batch creation fails
            ValidationError: If page data is invalid

        Example:
            >>> pages_to_create = [
            ...     PageCreate(title="Page 1", path="page-1", content="Content 1"),
            ...     PageCreate(title="Page 2", path="page-2", content="Content 2"),
            ...     PageCreate(title="Page 3", path="page-3", content="Content 3"),
            ... ]
            >>> created_pages = client.pages.create_many(pages_to_create)
            >>> print(f"Created {len(created_pages)} pages")
        """
        if not pages_data:
            return []

        created_pages = []
        errors = []

        for i, page_data in enumerate(pages_data):
            try:
                page = self.create(page_data)
                created_pages.append(page)
            except Exception as e:
                errors.append({"index": i, "data": page_data, "error": str(e)})

        if errors:
            # Include partial success information
            error_msg = f"Failed to create {len(errors)}/{len(pages_data)} pages. "
            error_msg += f"Successfully created: {len(created_pages)}. Errors: {errors}"
            raise APIError(error_msg)

        return created_pages

    def update_many(
        self, updates: List[Dict[str, Any]]
    ) -> List[Page]:
        """Update multiple pages in a single batch operation.

        Each update dict must contain an 'id' field and the fields to update.

        Args:
            updates: List of dicts with 'id' and update fields

        Returns:
            List of updated Page objects

        Raises:
            APIError: If batch update fails
            ValidationError: If update data is invalid

        Example:
            >>> updates = [
            ...     {"id": 1, "content": "New content 1"},
            ...     {"id": 2, "content": "New content 2", "title": "Updated Title"},
            ...     {"id": 3, "is_published": False},
            ... ]
            >>> updated_pages = client.pages.update_many(updates)
            >>> print(f"Updated {len(updated_pages)} pages")
        """
        if not updates:
            return []

        updated_pages = []
        errors = []

        for i, update_data in enumerate(updates):
            try:
                if "id" not in update_data:
                    raise ValidationError("Each update must have an 'id' field")

                page_id = update_data["id"]
                # Remove id from update data
                update_fields = {k: v for k, v in update_data.items() if k != "id"}

                page = self.update(page_id, update_fields)
                updated_pages.append(page)
            except Exception as e:
                errors.append({"index": i, "data": update_data, "error": str(e)})

        if errors:
            error_msg = f"Failed to update {len(errors)}/{len(updates)} pages. "
            error_msg += f"Successfully updated: {len(updated_pages)}. Errors: {errors}"
            raise APIError(error_msg)

        return updated_pages

    def delete_many(self, page_ids: List[int]) -> Dict[str, Any]:
        """Delete multiple pages in a single batch operation.

        Args:
            page_ids: List of page IDs to delete

        Returns:
            Dict with success count and any errors

        Raises:
            APIError: If batch deletion has errors
            ValidationError: If page IDs are invalid

        Example:
            >>> result = client.pages.delete_many([1, 2, 3, 4, 5])
            >>> print(f"Deleted {result['successful']} pages")
            >>> if result['failed']:
            ...     print(f"Failed: {result['errors']}")
        """
        if not page_ids:
            return {"successful": 0, "failed": 0, "errors": []}

        successful = 0
        errors = []

        for page_id in page_ids:
            try:
                self.delete(page_id)
                successful += 1
            except Exception as e:
                errors.append({"page_id": page_id, "error": str(e)})

        result = {
            "successful": successful,
            "failed": len(errors),
            "errors": errors,
        }

        if errors:
            error_msg = f"Failed to delete {len(errors)}/{len(page_ids)} pages. "
            error_msg += f"Successfully deleted: {successful}. Errors: {errors}"
            raise APIError(error_msg)

        return result
