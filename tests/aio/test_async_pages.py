"""Tests for AsyncPagesEndpoint."""

from unittest.mock import AsyncMock, Mock

import pytest

from wikijs.aio import AsyncWikiJSClient
from wikijs.aio.endpoints.pages import AsyncPagesEndpoint
from wikijs.exceptions import APIError, ValidationError
from wikijs.models.page import Page, PageCreate, PageUpdate


class TestAsyncPagesEndpoint:
    """Test suite for AsyncPagesEndpoint."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock async WikiJS client."""
        client = Mock(spec=AsyncWikiJSClient)
        return client

    @pytest.fixture
    def pages_endpoint(self, mock_client):
        """Create an AsyncPagesEndpoint instance with mock client."""
        return AsyncPagesEndpoint(mock_client)

    @pytest.fixture
    def sample_page_data(self):
        """Sample page data from API."""
        return {
            "id": 123,
            "title": "Test Page",
            "path": "test-page",
            "content": "# Test Page\n\nThis is test content.",
            "description": "A test page",
            "isPublished": True,
            "isPrivate": False,
            "tags": ["test", "example"],
            "locale": "en",
            "authorId": 1,
            "authorName": "Test User",
            "authorEmail": "test@example.com",
            "editor": "markdown",
            "createdAt": "2023-01-01T00:00:00Z",
            "updatedAt": "2023-01-02T00:00:00Z",
        }

    @pytest.fixture
    def sample_page_create(self):
        """Sample PageCreate object."""
        return PageCreate(
            title="New Page",
            path="new-page",
            content="# New Page\n\nContent here.",
            description="A new page",
            tags=["new", "test"],
        )

    @pytest.fixture
    def sample_page_update(self):
        """Sample PageUpdate object."""
        return PageUpdate(
            title="Updated Page",
            content="# Updated Page\n\nUpdated content.",
            tags=["updated", "test"],
        )

    def test_init(self, mock_client):
        """Test AsyncPagesEndpoint initialization."""
        endpoint = AsyncPagesEndpoint(mock_client)
        assert endpoint._client is mock_client

    @pytest.mark.asyncio
    async def test_list_basic(self, pages_endpoint, sample_page_data):
        """Test basic page listing."""
        # Mock the GraphQL response structure that matches Wiki.js schema
        mock_response = {"data": {"pages": {"list": [sample_page_data]}}}
        pages_endpoint._post = AsyncMock(return_value=mock_response)

        # Call list method
        pages = await pages_endpoint.list()

        # Verify request
        pages_endpoint._post.assert_called_once()
        call_args = pages_endpoint._post.call_args
        assert call_args[0][0] == "/graphql"

        # Verify response
        assert len(pages) == 1
        assert isinstance(pages[0], Page)
        assert pages[0].id == 123
        assert pages[0].title == "Test Page"
        assert pages[0].path == "test-page"

    @pytest.mark.asyncio
    async def test_list_with_parameters(self, pages_endpoint, sample_page_data):
        """Test page listing with filter parameters."""
        mock_response = {"data": {"pages": {"list": [sample_page_data]}}}
        pages_endpoint._post = AsyncMock(return_value=mock_response)

        # Call with parameters
        pages = await pages_endpoint.list(
            limit=10, offset=0, search="test", locale="en", order_by="title"
        )

        # Verify request
        call_args = pages_endpoint._post.call_args
        json_data = call_args[1]["json_data"]
        variables = json_data.get("variables", {})

        assert variables["limit"] == 10
        assert variables["offset"] == 0
        assert variables["search"] == "test"
        assert variables["locale"] == "en"
        assert variables["orderBy"] == "title"

        # Verify response
        assert len(pages) == 1

    @pytest.mark.asyncio
    async def test_list_validation_error(self, pages_endpoint):
        """Test validation errors in list method."""
        # Test invalid limit
        with pytest.raises(ValidationError, match="limit must be greater than 0"):
            await pages_endpoint.list(limit=0)

        # Test invalid offset
        with pytest.raises(ValidationError, match="offset must be non-negative"):
            await pages_endpoint.list(offset=-1)

        # Test invalid order_by
        with pytest.raises(
            ValidationError, match="order_by must be one of: title, created_at"
        ):
            await pages_endpoint.list(order_by="invalid")

    @pytest.mark.asyncio
    async def test_get_by_id(self, pages_endpoint, sample_page_data):
        """Test getting a page by ID."""
        mock_response = {"data": {"pages": {"single": sample_page_data}}}
        pages_endpoint._post = AsyncMock(return_value=mock_response)

        page = await pages_endpoint.get(123)

        # Verify request
        pages_endpoint._post.assert_called_once()
        call_args = pages_endpoint._post.call_args
        json_data = call_args[1]["json_data"]

        assert json_data["variables"]["id"] == 123

        # Verify response
        assert isinstance(page, Page)
        assert page.id == 123
        assert page.title == "Test Page"

    @pytest.mark.asyncio
    async def test_get_validation_error(self, pages_endpoint):
        """Test validation error for invalid page ID."""
        with pytest.raises(ValidationError, match="page_id must be a positive integer"):
            await pages_endpoint.get(0)

        with pytest.raises(ValidationError, match="page_id must be a positive integer"):
            await pages_endpoint.get(-1)

    @pytest.mark.asyncio
    async def test_get_not_found(self, pages_endpoint):
        """Test getting a non-existent page."""
        mock_response = {"data": {"pages": {"single": None}}}
        pages_endpoint._post = AsyncMock(return_value=mock_response)

        with pytest.raises(APIError, match="Page with ID 999 not found"):
            await pages_endpoint.get(999)

    @pytest.mark.asyncio
    async def test_get_by_path(self, pages_endpoint, sample_page_data):
        """Test getting a page by path."""
        mock_response = {"data": {"pageByPath": sample_page_data}}
        pages_endpoint._post = AsyncMock(return_value=mock_response)

        page = await pages_endpoint.get_by_path("test-page")

        # Verify request
        call_args = pages_endpoint._post.call_args
        json_data = call_args[1]["json_data"]
        variables = json_data["variables"]

        assert variables["path"] == "test-page"
        assert variables["locale"] == "en"

        # Verify response
        assert page.path == "test-page"

    @pytest.mark.asyncio
    async def test_create(self, pages_endpoint, sample_page_create, sample_page_data):
        """Test creating a new page."""
        mock_response = {
            "data": {
                "pages": {
                    "create": {
                        "responseResult": {"succeeded": True},
                        "page": sample_page_data,
                    }
                }
            }
        }
        pages_endpoint._post = AsyncMock(return_value=mock_response)

        page = await pages_endpoint.create(sample_page_create)

        # Verify request
        call_args = pages_endpoint._post.call_args
        json_data = call_args[1]["json_data"]
        variables = json_data["variables"]

        assert variables["title"] == "New Page"
        assert variables["path"] == "new-page"
        assert variables["content"] == "# New Page\n\nContent here."

        # Verify response
        assert isinstance(page, Page)
        assert page.id == 123

    @pytest.mark.asyncio
    async def test_create_failure(self, pages_endpoint, sample_page_create):
        """Test failed page creation."""
        mock_response = {
            "data": {
                "pages": {
                    "create": {
                        "responseResult": {"succeeded": False, "message": "Error creating page"},
                        "page": None,
                    }
                }
            }
        }
        pages_endpoint._post = AsyncMock(return_value=mock_response)

        with pytest.raises(APIError, match="Page creation failed"):
            await pages_endpoint.create(sample_page_create)

    @pytest.mark.asyncio
    async def test_update(self, pages_endpoint, sample_page_update, sample_page_data):
        """Test updating an existing page."""
        updated_data = sample_page_data.copy()
        updated_data["title"] = "Updated Page"

        mock_response = {"data": {"updatePage": updated_data}}
        pages_endpoint._post = AsyncMock(return_value=mock_response)

        page = await pages_endpoint.update(123, sample_page_update)

        # Verify request
        call_args = pages_endpoint._post.call_args
        json_data = call_args[1]["json_data"]
        variables = json_data["variables"]

        assert variables["id"] == 123
        assert variables["title"] == "Updated Page"

        # Verify response
        assert isinstance(page, Page)
        assert page.id == 123

    @pytest.mark.asyncio
    async def test_delete(self, pages_endpoint):
        """Test deleting a page."""
        mock_response = {"data": {"deletePage": {"success": True}}}
        pages_endpoint._post = AsyncMock(return_value=mock_response)

        result = await pages_endpoint.delete(123)

        # Verify request
        call_args = pages_endpoint._post.call_args
        json_data = call_args[1]["json_data"]

        assert json_data["variables"]["id"] == 123

        # Verify response
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_failure(self, pages_endpoint):
        """Test failed page deletion."""
        mock_response = {
            "data": {"deletePage": {"success": False, "message": "Page not found"}}
        }
        pages_endpoint._post = AsyncMock(return_value=mock_response)

        with pytest.raises(APIError, match="Page deletion failed"):
            await pages_endpoint.delete(123)

    @pytest.mark.asyncio
    async def test_search(self, pages_endpoint, sample_page_data):
        """Test searching for pages."""
        mock_response = {"data": {"pages": {"list": [sample_page_data]}}}
        pages_endpoint._post = AsyncMock(return_value=mock_response)

        pages = await pages_endpoint.search("test query", limit=10)

        # Verify that search uses list method with search parameter
        call_args = pages_endpoint._post.call_args
        json_data = call_args[1]["json_data"]
        variables = json_data.get("variables", {})

        assert variables["search"] == "test query"
        assert variables["limit"] == 10

        assert len(pages) == 1

    @pytest.mark.asyncio
    async def test_get_by_tags(self, pages_endpoint, sample_page_data):
        """Test getting pages by tags."""
        mock_response = {"data": {"pages": {"list": [sample_page_data]}}}
        pages_endpoint._post = AsyncMock(return_value=mock_response)

        pages = await pages_endpoint.get_by_tags(["test", "example"], match_all=True)

        # Verify request
        call_args = pages_endpoint._post.call_args
        json_data = call_args[1]["json_data"]
        variables = json_data.get("variables", {})

        assert variables["tags"] == ["test", "example"]

        assert len(pages) == 1

    @pytest.mark.asyncio
    async def test_graphql_error(self, pages_endpoint):
        """Test handling GraphQL errors."""
        mock_response = {"errors": [{"message": "GraphQL Error"}]}
        pages_endpoint._post = AsyncMock(return_value=mock_response)

        with pytest.raises(APIError, match="GraphQL errors"):
            await pages_endpoint.list()

    def test_normalize_page_data(self, pages_endpoint, sample_page_data):
        """Test page data normalization."""
        normalized = pages_endpoint._normalize_page_data(sample_page_data)

        assert normalized["id"] == 123
        assert normalized["title"] == "Test Page"
        assert normalized["is_published"] is True
        assert normalized["is_private"] is False
        assert normalized["author_id"] == 1
        assert normalized["author_name"] == "Test User"
        assert normalized["tags"] == ["test", "example"]

    def test_normalize_page_data_with_tag_objects(self, pages_endpoint):
        """Test normalizing page data with tag objects."""
        page_data = {
            "id": 123,
            "title": "Test",
            "tags": [{"tag": "test1"}, {"tag": "test2"}],
        }

        normalized = pages_endpoint._normalize_page_data(page_data)

        assert normalized["tags"] == ["test1", "test2"]
