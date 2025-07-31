"""Tests for Pages API endpoint."""

from unittest.mock import Mock, patch

import pytest

from wikijs.client import WikiJSClient
from wikijs.endpoints.pages import PagesEndpoint
from wikijs.exceptions import APIError, ValidationError
from wikijs.models.page import Page, PageCreate, PageUpdate


class TestPagesEndpoint:
    """Test suite for PagesEndpoint."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock WikiJS client."""
        client = Mock(spec=WikiJSClient)
        return client

    @pytest.fixture
    def pages_endpoint(self, mock_client):
        """Create a PagesEndpoint instance with mock client."""
        return PagesEndpoint(mock_client)

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
        """Test PagesEndpoint initialization."""
        endpoint = PagesEndpoint(mock_client)
        assert endpoint._client is mock_client

    def test_list_basic(self, pages_endpoint, sample_page_data):
        """Test basic page listing."""
        # Mock the GraphQL response
        mock_response = {"data": {"pages": [sample_page_data]}}
        pages_endpoint._post = Mock(return_value=mock_response)

        # Call list method
        pages = pages_endpoint.list()

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

    def test_list_with_parameters(self, pages_endpoint, sample_page_data):
        """Test page listing with filter parameters."""
        mock_response = {"data": {"pages": [sample_page_data]}}
        pages_endpoint._post = Mock(return_value=mock_response)

        # Call with parameters
        pages = pages_endpoint.list(
            limit=10,
            offset=5,
            search="test",
            tags=["test"],
            locale="en",
            author_id=1,
            order_by="created_at",
            order_direction="DESC",
        )

        # Verify request
        call_args = pages_endpoint._post.call_args
        query_data = call_args[1]["json_data"]
        variables = query_data["variables"]

        assert variables["limit"] == 10
        assert variables["offset"] == 5
        assert variables["search"] == "test"
        assert variables["tags"] == ["test"]
        assert variables["locale"] == "en"
        assert variables["authorId"] == 1
        assert variables["orderBy"] == "created_at"
        assert variables["orderDirection"] == "DESC"

        # Verify response
        assert len(pages) == 1
        assert isinstance(pages[0], Page)

    def test_list_validation_errors(self, pages_endpoint):
        """Test list method parameter validation."""
        # Test invalid limit
        with pytest.raises(ValidationError, match="limit must be greater than 0"):
            pages_endpoint.list(limit=0)

        # Test invalid offset
        with pytest.raises(ValidationError, match="offset must be non-negative"):
            pages_endpoint.list(offset=-1)

        # Test invalid order_by
        with pytest.raises(ValidationError, match="order_by must be one of"):
            pages_endpoint.list(order_by="invalid")

        # Test invalid order_direction
        with pytest.raises(
            ValidationError, match="order_direction must be ASC or DESC"
        ):
            pages_endpoint.list(order_direction="INVALID")

    def test_list_api_error(self, pages_endpoint):
        """Test list method handling API errors."""
        # Mock GraphQL error response
        mock_response = {"errors": [{"message": "GraphQL error"}]}
        pages_endpoint._post = Mock(return_value=mock_response)

        with pytest.raises(APIError, match="GraphQL errors"):
            pages_endpoint.list()

    def test_get_success(self, pages_endpoint, sample_page_data):
        """Test getting a page by ID."""
        mock_response = {"data": {"page": sample_page_data}}
        pages_endpoint._post = Mock(return_value=mock_response)

        # Call method
        page = pages_endpoint.get(123)

        # Verify request
        call_args = pages_endpoint._post.call_args
        query_data = call_args[1]["json_data"]
        assert query_data["variables"]["id"] == 123

        # Verify response
        assert isinstance(page, Page)
        assert page.id == 123
        assert page.title == "Test Page"

    def test_get_validation_error(self, pages_endpoint):
        """Test get method parameter validation."""
        with pytest.raises(ValidationError, match="page_id must be a positive integer"):
            pages_endpoint.get(0)

        with pytest.raises(ValidationError, match="page_id must be a positive integer"):
            pages_endpoint.get(-1)

        with pytest.raises(ValidationError, match="page_id must be a positive integer"):
            pages_endpoint.get("invalid")

    def test_get_not_found(self, pages_endpoint):
        """Test get method when page not found."""
        mock_response = {"data": {"page": None}}
        pages_endpoint._post = Mock(return_value=mock_response)

        with pytest.raises(APIError, match="Page with ID 123 not found"):
            pages_endpoint.get(123)

    def test_get_by_path_success(self, pages_endpoint, sample_page_data):
        """Test getting a page by path."""
        mock_response = {"data": {"pageByPath": sample_page_data}}
        pages_endpoint._post = Mock(return_value=mock_response)

        # Call method
        page = pages_endpoint.get_by_path("test-page")

        # Verify request
        call_args = pages_endpoint._post.call_args
        query_data = call_args[1]["json_data"]
        variables = query_data["variables"]
        assert variables["path"] == "test-page"
        assert variables["locale"] == "en"

        # Verify response
        assert isinstance(page, Page)
        assert page.path == "test-page"

    def test_get_by_path_validation_error(self, pages_endpoint):
        """Test get_by_path method parameter validation."""
        with pytest.raises(ValidationError, match="path must be a non-empty string"):
            pages_endpoint.get_by_path("")

        with pytest.raises(ValidationError, match="path must be a non-empty string"):
            pages_endpoint.get_by_path(None)

    def test_create_success(self, pages_endpoint, sample_page_create, sample_page_data):
        """Test creating a new page."""
        mock_response = {"data": {"createPage": sample_page_data}}
        pages_endpoint._post = Mock(return_value=mock_response)

        # Call method
        created_page = pages_endpoint.create(sample_page_create)

        # Verify request
        call_args = pages_endpoint._post.call_args
        query_data = call_args[1]["json_data"]
        variables = query_data["variables"]

        assert variables["title"] == "New Page"
        assert variables["path"] == "new-page"
        assert variables["content"] == "# New Page\n\nContent here."
        assert variables["description"] == "A new page"
        assert variables["tags"] == ["new", "test"]
        assert variables["isPublished"] is True
        assert variables["isPrivate"] is False

        # Verify response
        assert isinstance(created_page, Page)
        assert created_page.id == 123

    def test_create_with_dict(self, pages_endpoint, sample_page_data):
        """Test creating a page with dict data."""
        mock_response = {"data": {"createPage": sample_page_data}}
        pages_endpoint._post = Mock(return_value=mock_response)

        page_dict = {
            "title": "Dict Page",
            "path": "dict-page",
            "content": "Content from dict",
        }

        # Call method
        created_page = pages_endpoint.create(page_dict)

        # Verify response
        assert isinstance(created_page, Page)

    def test_create_validation_error(self, pages_endpoint):
        """Test create method validation errors."""
        # Test invalid data type
        with pytest.raises(
            ValidationError,
            match="page_data must be PageCreate object or dict",
        ):
            pages_endpoint.create("invalid")

        # Test invalid dict data
        with pytest.raises(ValidationError, match="Invalid page data"):
            pages_endpoint.create({"invalid": "data"})

    def test_create_api_error(self, pages_endpoint, sample_page_create):
        """Test create method API errors."""
        mock_response = {"errors": [{"message": "Creation failed"}]}
        pages_endpoint._post = Mock(return_value=mock_response)

        with pytest.raises(APIError, match="Failed to create page"):
            pages_endpoint.create(sample_page_create)

    def test_update_success(self, pages_endpoint, sample_page_update, sample_page_data):
        """Test updating a page."""
        mock_response = {"data": {"updatePage": sample_page_data}}
        pages_endpoint._post = Mock(return_value=mock_response)

        # Call method
        updated_page = pages_endpoint.update(123, sample_page_update)

        # Verify request
        call_args = pages_endpoint._post.call_args
        query_data = call_args[1]["json_data"]
        variables = query_data["variables"]

        assert variables["id"] == 123
        assert variables["title"] == "Updated Page"
        assert variables["content"] == "# Updated Page\n\nUpdated content."
        assert variables["tags"] == ["updated", "test"]
        assert "description" not in variables  # Should not include None values

        # Verify response
        assert isinstance(updated_page, Page)

    def test_update_validation_errors(self, pages_endpoint, sample_page_update):
        """Test update method validation errors."""
        # Test invalid page_id
        with pytest.raises(ValidationError, match="page_id must be a positive integer"):
            pages_endpoint.update(0, sample_page_update)

        # Test invalid page_data type
        with pytest.raises(
            ValidationError,
            match="page_data must be PageUpdate object or dict",
        ):
            pages_endpoint.update(123, "invalid")

    def test_delete_success(self, pages_endpoint):
        """Test deleting a page."""
        mock_response = {
            "data": {
                "deletePage": {
                    "success": True,
                    "message": "Page deleted successfully",
                }
            }
        }
        pages_endpoint._post = Mock(return_value=mock_response)

        # Call method
        result = pages_endpoint.delete(123)

        # Verify request
        call_args = pages_endpoint._post.call_args
        query_data = call_args[1]["json_data"]
        assert query_data["variables"]["id"] == 123

        # Verify response
        assert result is True

    def test_delete_validation_error(self, pages_endpoint):
        """Test delete method validation errors."""
        with pytest.raises(ValidationError, match="page_id must be a positive integer"):
            pages_endpoint.delete(0)

    def test_delete_failure(self, pages_endpoint):
        """Test delete method when deletion fails."""
        mock_response = {
            "data": {"deletePage": {"success": False, "message": "Deletion failed"}}
        }
        pages_endpoint._post = Mock(return_value=mock_response)

        with pytest.raises(APIError, match="Page deletion failed: Deletion failed"):
            pages_endpoint.delete(123)

    def test_search_success(self, pages_endpoint, sample_page_data):
        """Test searching pages."""
        mock_response = {"data": {"pages": [sample_page_data]}}
        pages_endpoint._post = Mock(return_value=mock_response)

        # Call method
        results = pages_endpoint.search("test query", limit=5)

        # Verify request (should call list with search parameter)
        call_args = pages_endpoint._post.call_args
        query_data = call_args[1]["json_data"]
        variables = query_data["variables"]

        assert variables["search"] == "test query"
        assert variables["limit"] == 5

        # Verify response
        assert len(results) == 1
        assert isinstance(results[0], Page)

    def test_search_validation_error(self, pages_endpoint):
        """Test search method validation errors."""
        with pytest.raises(ValidationError, match="query must be a non-empty string"):
            pages_endpoint.search("")

        with pytest.raises(ValidationError, match="limit must be greater than 0"):
            pages_endpoint.search("test", limit=0)

    def test_get_by_tags_match_all(self, pages_endpoint, sample_page_data):
        """Test getting pages by tags (match all)."""
        mock_response = {"data": {"pages": [sample_page_data]}}
        pages_endpoint._post = Mock(return_value=mock_response)

        # Call method
        results = pages_endpoint.get_by_tags(["test", "example"], match_all=True)

        # Verify request (should call list with tags parameter)
        call_args = pages_endpoint._post.call_args
        query_data = call_args[1]["json_data"]
        variables = query_data["variables"]

        assert variables["tags"] == ["test", "example"]

        # Verify response
        assert len(results) == 1
        assert isinstance(results[0], Page)

    def test_get_by_tags_validation_error(self, pages_endpoint):
        """Test get_by_tags method validation errors."""
        with pytest.raises(ValidationError, match="tags must be a non-empty list"):
            pages_endpoint.get_by_tags([])

        with pytest.raises(ValidationError, match="limit must be greater than 0"):
            pages_endpoint.get_by_tags(["test"], limit=0)

    def test_normalize_page_data(self, pages_endpoint):
        """Test page data normalization."""
        api_data = {
            "id": 123,
            "title": "Test",
            "isPublished": True,
            "authorId": 1,
            "createdAt": "2023-01-01T00:00:00Z",
        }

        normalized = pages_endpoint._normalize_page_data(api_data)

        # Check field mapping
        assert normalized["id"] == 123
        assert normalized["title"] == "Test"
        assert normalized["is_published"] is True
        assert normalized["author_id"] == 1
        assert normalized["created_at"] == "2023-01-01T00:00:00Z"
        assert normalized["tags"] == []  # Default value

    def test_normalize_page_data_missing_fields(self, pages_endpoint):
        """Test page data normalization with missing fields."""
        api_data = {"id": 123, "title": "Test"}

        normalized = pages_endpoint._normalize_page_data(api_data)

        # Check that only present fields are included
        assert "id" in normalized
        assert "title" in normalized
        assert "is_published" not in normalized
        assert "tags" in normalized  # Should have default value

    @patch("wikijs.endpoints.pages.Page")
    def test_list_page_parsing_error(
        self, mock_page_class, pages_endpoint, sample_page_data
    ):
        """Test handling of page parsing errors in list method."""
        # Mock Page constructor to raise an exception
        mock_page_class.side_effect = ValueError("Parsing error")

        mock_response = {"data": {"pages": [sample_page_data]}}
        pages_endpoint._post = Mock(return_value=mock_response)

        with pytest.raises(APIError, match="Failed to parse page data"):
            pages_endpoint.list()

    def test_graphql_query_structure(self, pages_endpoint, sample_page_data):
        """Test that GraphQL queries have correct structure."""
        mock_response = {"data": {"pages": [sample_page_data]}}
        pages_endpoint._post = Mock(return_value=mock_response)

        # Call list method
        pages_endpoint.list()

        # Verify the GraphQL query structure
        call_args = pages_endpoint._post.call_args
        query_data = call_args[1]["json_data"]

        assert "query" in query_data
        assert "variables" in query_data
        assert "pages(" in query_data["query"]
        assert "id" in query_data["query"]
        assert "title" in query_data["query"]
        assert "content" in query_data["query"]
