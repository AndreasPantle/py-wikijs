"""Test configuration and fixtures for wikijs-python-sdk."""

import pytest
import responses

from wikijs.auth import APIKeyAuth, JWTAuth, NoAuth


@pytest.fixture
def mock_api_key():
    """Fixture providing a test API key."""
    return "test-api-key-12345"


@pytest.fixture
def mock_jwt_token():
    """Fixture providing a test JWT token."""
    return "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIiwiYWRtaW4iOnRydWV9.TJVA95OrM7E2cBab30RMHrHDcEfxjoYZgeFONFh7HgQ"


@pytest.fixture
def api_key_auth(mock_api_key):
    """Fixture providing APIKeyAuth instance."""
    return APIKeyAuth(mock_api_key)


@pytest.fixture
def jwt_auth(mock_jwt_token, mock_wiki_base_url):
    """Fixture providing JWTAuth instance."""
    return JWTAuth(mock_jwt_token, mock_wiki_base_url)


@pytest.fixture
def no_auth():
    """Fixture providing NoAuth instance."""
    return NoAuth()


@pytest.fixture
def mock_wiki_base_url():
    """Fixture providing test Wiki.js base URL."""
    return "https://wiki.example.com"


@pytest.fixture
def mock_responses():
    """Fixture providing responses mock for HTTP requests."""
    with responses.RequestsMock() as rsps:
        yield rsps


@pytest.fixture
def sample_page_data():
    """Fixture providing sample page data."""
    return {
        "id": 1,
        "title": "Test Page",
        "path": "test-page",
        "content": "This is a test page content.",
        "created_at": "2023-01-01T00:00:00Z",
        "updated_at": "2023-01-01T12:00:00Z",
        "author": {"id": 1, "name": "Test User", "email": "test@example.com"},
        "tags": ["test", "example"],
    }


@pytest.fixture
def sample_error_response():
    """Fixture providing sample error response."""
    return {"error": {"message": "Not found", "code": "PAGE_NOT_FOUND"}}
