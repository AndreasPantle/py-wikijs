"""Tests for Pages API batch operations."""

import pytest
import responses

from wikijs import WikiJSClient
from wikijs.exceptions import APIError, ValidationError
from wikijs.models import Page, PageCreate, PageUpdate


@pytest.fixture
def client():
    """Create a test client."""
    return WikiJSClient("https://wiki.example.com", auth="test-api-key")


class TestPagesCreateMany:
    """Tests for pages.create_many() method."""

    @responses.activate
    def test_create_many_success(self, client):
        """Test successful batch page creation."""
        # Mock API responses for each create
        for i in range(1, 4):
            responses.add(
                responses.POST,
                "https://wiki.example.com/graphql",
                json={
                    "data": {
                        "pages": {
                            "create": {
                                "responseResult": {"succeeded": True},
                                "page": {
                                    "id": i,
                                    "title": f"Page {i}",
                                    "path": f"page-{i}",
                                    "content": f"Content {i}",
                                    "description": "",
                                    "isPublished": True,
                                    "isPrivate": False,
                                    "tags": [],
                                    "locale": "en",
                                    "authorId": 1,
                                    "authorName": "Admin",
                                    "authorEmail": "admin@example.com",
                                    "editor": "markdown",
                                    "createdAt": "2025-01-01T00:00:00.000Z",
                                    "updatedAt": "2025-01-01T00:00:00.000Z",
                                },
                            }
                        }
                    }
                },
                status=200,
            )

        pages_data = [
            PageCreate(title=f"Page {i}", path=f"page-{i}", content=f"Content {i}")
            for i in range(1, 4)
        ]

        created_pages = client.pages.create_many(pages_data)

        assert len(created_pages) == 3
        for i, page in enumerate(created_pages, 1):
            assert page.id == i
            assert page.title == f"Page {i}"

    def test_create_many_empty_list(self, client):
        """Test create_many with empty list."""
        result = client.pages.create_many([])
        assert result == []

    @responses.activate
    def test_create_many_partial_failure(self, client):
        """Test create_many with some failures."""
        # Mock successful creation for first page
        responses.add(
            responses.POST,
            "https://wiki.example.com/graphql",
            json={
                "data": {
                    "pages": {
                        "create": {
                            "responseResult": {"succeeded": True},
                            "page": {
                                "id": 1,
                                "title": "Page 1",
                                "path": "page-1",
                                "content": "Content 1",
                                "description": "",
                                "isPublished": True,
                                "isPrivate": False,
                                "tags": [],
                                "locale": "en",
                                "authorId": 1,
                                "authorName": "Admin",
                                "authorEmail": "admin@example.com",
                                "editor": "markdown",
                                "createdAt": "2025-01-01T00:00:00.000Z",
                                "updatedAt": "2025-01-01T00:00:00.000Z",
                            },
                        }
                    }
                }
            },
            status=200,
        )

        # Mock failure for second page
        responses.add(
            responses.POST,
            "https://wiki.example.com/graphql",
            json={"errors": [{"message": "Page already exists"}]},
            status=200,
        )

        pages_data = [
            PageCreate(title="Page 1", path="page-1", content="Content 1"),
            PageCreate(title="Page 2", path="page-2", content="Content 2"),
        ]

        with pytest.raises(APIError) as exc_info:
            client.pages.create_many(pages_data)

        assert "Failed to create 1/2 pages" in str(exc_info.value)
        assert "Successfully created: 1" in str(exc_info.value)


class TestPagesUpdateMany:
    """Tests for pages.update_many() method."""

    @responses.activate
    def test_update_many_success(self, client):
        """Test successful batch page updates."""
        # Mock API responses for each update
        for i in range(1, 4):
            responses.add(
                responses.POST,
                "https://wiki.example.com/graphql",
                json={
                    "data": {
                        "updatePage": {
                            "id": i,
                            "title": f"Updated Page {i}",
                            "path": f"page-{i}",
                            "content": f"Updated Content {i}",
                            "description": "",
                            "isPublished": True,
                            "isPrivate": False,
                            "tags": [],
                            "locale": "en",
                            "authorId": 1,
                            "authorName": "Admin",
                            "authorEmail": "admin@example.com",
                            "editor": "markdown",
                            "createdAt": "2025-01-01T00:00:00.000Z",
                            "updatedAt": "2025-01-01T00:10:00.000Z",
                        }
                    }
                },
                status=200,
            )

        updates = [
            {"id": i, "content": f"Updated Content {i}", "title": f"Updated Page {i}"}
            for i in range(1, 4)
        ]

        updated_pages = client.pages.update_many(updates)

        assert len(updated_pages) == 3
        for i, page in enumerate(updated_pages, 1):
            assert page.id == i
            assert page.title == f"Updated Page {i}"
            assert page.content == f"Updated Content {i}"

    def test_update_many_empty_list(self, client):
        """Test update_many with empty list."""
        result = client.pages.update_many([])
        assert result == []

    def test_update_many_missing_id(self, client):
        """Test update_many with missing id field."""
        updates = [{"content": "New content"}]  # Missing 'id'

        with pytest.raises(APIError) as exc_info:
            client.pages.update_many(updates)

        assert "must have an 'id' field" in str(exc_info.value)

    @responses.activate
    def test_update_many_partial_failure(self, client):
        """Test update_many with some failures."""
        # Mock successful update for first page
        responses.add(
            responses.POST,
            "https://wiki.example.com/graphql",
            json={
                "data": {
                    "updatePage": {
                        "id": 1,
                        "title": "Updated Page 1",
                        "path": "page-1",
                        "content": "Updated Content 1",
                        "description": "",
                        "isPublished": True,
                        "isPrivate": False,
                        "tags": [],
                        "locale": "en",
                        "authorId": 1,
                        "authorName": "Admin",
                        "authorEmail": "admin@example.com",
                        "editor": "markdown",
                        "createdAt": "2025-01-01T00:00:00.000Z",
                        "updatedAt": "2025-01-01T00:10:00.000Z",
                    }
                }
            },
            status=200,
        )

        # Mock failure for second page
        responses.add(
            responses.POST,
            "https://wiki.example.com/graphql",
            json={"errors": [{"message": "Page not found"}]},
            status=200,
        )

        updates = [
            {"id": 1, "content": "Updated Content 1"},
            {"id": 999, "content": "Updated Content 999"},
        ]

        with pytest.raises(APIError) as exc_info:
            client.pages.update_many(updates)

        assert "Failed to update 1/2 pages" in str(exc_info.value)


class TestPagesDeleteMany:
    """Tests for pages.delete_many() method."""

    @responses.activate
    def test_delete_many_success(self, client):
        """Test successful batch page deletions."""
        # Mock API responses for each delete
        for i in range(1, 4):
            responses.add(
                responses.POST,
                "https://wiki.example.com/graphql",
                json={"data": {"deletePage": {"success": True}}},
                status=200,
            )

        result = client.pages.delete_many([1, 2, 3])

        assert result["successful"] == 3
        assert result["failed"] == 0
        assert result["errors"] == []

    def test_delete_many_empty_list(self, client):
        """Test delete_many with empty list."""
        result = client.pages.delete_many([])
        assert result["successful"] == 0
        assert result["failed"] == 0
        assert result["errors"] == []

    @responses.activate
    def test_delete_many_partial_failure(self, client):
        """Test delete_many with some failures."""
        # Mock successful deletion for first two pages
        responses.add(
            responses.POST,
            "https://wiki.example.com/graphql",
            json={"data": {"deletePage": {"success": True}}},
            status=200,
        )
        responses.add(
            responses.POST,
            "https://wiki.example.com/graphql",
            json={"data": {"deletePage": {"success": True}}},
            status=200,
        )

        # Mock failure for third page
        responses.add(
            responses.POST,
            "https://wiki.example.com/graphql",
            json={"errors": [{"message": "Page not found"}]},
            status=200,
        )

        with pytest.raises(APIError) as exc_info:
            client.pages.delete_many([1, 2, 999])

        assert "Failed to delete 1/3 pages" in str(exc_info.value)
        assert "Successfully deleted: 2" in str(exc_info.value)
