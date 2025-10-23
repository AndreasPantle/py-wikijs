"""Tests for WikiJS client."""

import json
from unittest.mock import Mock, patch

import pytest

from wikijs.auth import APIKeyAuth
from wikijs.client import WikiJSClient
from wikijs.exceptions import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    ConnectionError,
    TimeoutError,
)


class TestWikiJSClientInit:
    """Test WikiJSClient initialization."""

    def test_init_with_api_key_string(self):
        """Test initialization with API key string."""
        with patch("wikijs.client.requests.Session"):
            client = WikiJSClient("https://wiki.example.com", auth="test-key")

            assert client.base_url == "https://wiki.example.com"
            assert isinstance(client._auth_handler, APIKeyAuth)
            assert client.timeout == 30
            assert client.verify_ssl is True
            assert "py-wikijs" in client.user_agent

    def test_init_with_auth_handler(self):
        """Test initialization with auth handler."""
        auth_handler = APIKeyAuth("test-key")

        with patch("wikijs.client.requests.Session"):
            client = WikiJSClient("https://wiki.example.com", auth=auth_handler)

            assert client._auth_handler is auth_handler

    def test_init_invalid_auth(self):
        """Test initialization with invalid auth parameter."""
        with pytest.raises(ConfigurationError, match="Invalid auth parameter"):
            WikiJSClient("https://wiki.example.com", auth=123)

    def test_init_with_custom_settings(self):
        """Test initialization with custom settings."""
        with patch("wikijs.client.requests.Session"):
            client = WikiJSClient(
                "https://wiki.example.com",
                auth="test-key",
                timeout=60,
                verify_ssl=False,
                user_agent="Custom Agent",
            )

            assert client.timeout == 60
            assert client.verify_ssl is False
            assert client.user_agent == "Custom Agent"

    def test_has_pages_endpoint(self):
        """Test that client has pages endpoint."""
        with patch("wikijs.client.requests.Session"):
            client = WikiJSClient("https://wiki.example.com", auth="test-key")

            assert hasattr(client, "pages")
            assert client.pages._client is client


class TestWikiJSClientTestConnection:
    """Test WikiJSClient connection testing."""

    @pytest.fixture
    def mock_wiki_base_url(self):
        """Mock wiki base URL."""
        return "https://wiki.example.com"

    @pytest.fixture
    def mock_api_key(self):
        """Mock API key."""
        return "test-api-key-12345"

    @patch("wikijs.client.requests.Session.request")
    def test_test_connection_success(self, mock_request, mock_wiki_base_url, mock_api_key):
        """Test successful connection test using GraphQL query."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "data": {
                "site": {
                    "title": "Test Wiki"
                }
            }
        }
        mock_request.return_value = mock_response

        client = WikiJSClient(mock_wiki_base_url, auth=mock_api_key)
        result = client.test_connection()

        assert result is True
        # Verify it made a POST request to GraphQL endpoint
        mock_request.assert_called_once()

    @patch("wikijs.client.requests.Session.request")
    def test_test_connection_timeout(self, mock_request, mock_wiki_base_url, mock_api_key):
        """Test connection test timeout."""
        import requests

        mock_request.side_effect = requests.exceptions.Timeout("Request timed out")

        client = WikiJSClient(mock_wiki_base_url, auth=mock_api_key)

        with pytest.raises(TimeoutError):
            client.test_connection()

    @patch("wikijs.client.requests.Session.request")
    def test_test_connection_error(self, mock_request, mock_wiki_base_url, mock_api_key):
        """Test connection test with connection error."""
        import requests

        mock_request.side_effect = requests.exceptions.ConnectionError("Connection failed")

        client = WikiJSClient(mock_wiki_base_url, auth=mock_api_key)

        with pytest.raises(ConnectionError):
            client.test_connection()

    def test_test_connection_no_base_url(self):
        """Test connection test with no base URL."""
        with patch("wikijs.client.requests.Session"):
            client = WikiJSClient("https://wiki.example.com", auth="test-key")
            client.base_url = ""  # Simulate empty base URL after creation

            with pytest.raises(ConfigurationError, match="Base URL not configured"):
                client.test_connection()

    def test_test_connection_no_auth(self):
        """Test connection test with no auth."""
        with patch("wikijs.client.requests.Session"):
            client = WikiJSClient("https://wiki.example.com", auth="test-key")
            client._auth_handler = None  # Simulate no auth

            with pytest.raises(
                ConfigurationError, match="Authentication not configured"
            ):
                client.test_connection()


class TestWikiJSClientRequests:
    """Test WikiJSClient HTTP request handling."""

    @pytest.fixture
    def mock_wiki_base_url(self):
        """Mock wiki base URL."""
        return "https://wiki.example.com"

    @pytest.fixture
    def mock_api_key(self):
        """Mock API key."""
        return "test-api-key-12345"

    @patch("wikijs.client.requests.Session.request")
    def test_request_success(self, mock_request, mock_wiki_base_url, mock_api_key):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"data": "test"}
        mock_request.return_value = mock_response

        client = WikiJSClient(mock_wiki_base_url, auth=mock_api_key)
        result = client._request("GET", "/test")

        assert result == {"data": "test"}
        mock_request.assert_called_once()

    @patch("wikijs.client.requests.Session.request")
    def test_request_with_json_data(
        self, mock_request, mock_wiki_base_url, mock_api_key
    ):
        """Test API request with JSON data."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"success": True}
        mock_request.return_value = mock_response

        client = WikiJSClient(mock_wiki_base_url, auth=mock_api_key)
        result = client._request("POST", "/test", json_data={"title": "Test"})

        assert result == {"success": True}
        mock_request.assert_called_once()

    @patch("wikijs.client.requests.Session.request")
    def test_request_authentication_error(
        self, mock_request, mock_wiki_base_url, mock_api_key
    ):
        """Test request with authentication error."""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 401
        mock_request.return_value = mock_response

        client = WikiJSClient(mock_wiki_base_url, auth=mock_api_key)

        with pytest.raises(AuthenticationError, match="Authentication failed"):
            client._request("GET", "/test")

    @patch("wikijs.client.requests.Session.request")
    def test_request_api_error(self, mock_request, mock_wiki_base_url, mock_api_key):
        """Test request with API error."""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.text = "Not found"
        mock_request.return_value = mock_response

        client = WikiJSClient(mock_wiki_base_url, auth=mock_api_key)

        with pytest.raises(APIError):
            client._request("GET", "/test")

    @patch("wikijs.client.requests.Session.request")
    def test_request_invalid_json_response(
        self, mock_request, mock_wiki_base_url, mock_api_key
    ):
        """Test request with invalid JSON response."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.side_effect = json.JSONDecodeError("Invalid JSON", "", 0)
        mock_request.return_value = mock_response

        client = WikiJSClient(mock_wiki_base_url, auth=mock_api_key)

        with pytest.raises(APIError, match="Invalid JSON response"):
            client._request("GET", "/test")

    @patch("wikijs.client.requests.Session.request")
    def test_request_timeout(self, mock_request, mock_wiki_base_url, mock_api_key):
        """Test request timeout handling."""
        import requests

        mock_request.side_effect = requests.exceptions.Timeout("Request timed out")

        client = WikiJSClient(mock_wiki_base_url, auth=mock_api_key)

        with pytest.raises(TimeoutError, match="Request timed out"):
            client._request("GET", "/test")

    @patch("wikijs.client.requests.Session.request")
    def test_request_connection_error(
        self, mock_request, mock_wiki_base_url, mock_api_key
    ):
        """Test request connection error handling."""
        import requests

        mock_request.side_effect = requests.exceptions.ConnectionError(
            "Connection failed"
        )

        client = WikiJSClient(mock_wiki_base_url, auth=mock_api_key)

        with pytest.raises(ConnectionError, match="Failed to connect"):
            client._request("GET", "/test")

    @patch("wikijs.client.requests.Session.request")
    def test_request_general_exception(
        self, mock_request, mock_wiki_base_url, mock_api_key
    ):
        """Test request general exception handling."""
        import requests

        mock_request.side_effect = requests.exceptions.RequestException("General error")

        client = WikiJSClient(mock_wiki_base_url, auth=mock_api_key)

        with pytest.raises(APIError, match="Request failed"):
            client._request("GET", "/test")


class TestWikiJSClientWithDifferentAuth:
    """Test WikiJSClient with different auth types."""

    @patch("wikijs.client.requests.Session")
    def test_auth_validation_during_session_creation(self, mock_session_class):
        """Test that auth validation happens during session creation."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        # Mock auth handler that raises validation error during validation
        from wikijs.auth.base import AuthHandler
        from wikijs.exceptions import AuthenticationError

        mock_auth = Mock(spec=AuthHandler)
        mock_auth.validate_credentials.side_effect = AuthenticationError(
            "Invalid credentials"
        )
        mock_auth.get_headers.return_value = {}

        with pytest.raises(AuthenticationError, match="Invalid credentials"):
            WikiJSClient("https://wiki.example.com", auth=mock_auth)


class TestWikiJSClientContextManager:
    """Test WikiJSClient context manager functionality."""

    @patch("wikijs.client.requests.Session")
    def test_context_manager(self, mock_session_class):
        """Test client as context manager."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        with WikiJSClient("https://wiki.example.com", auth="test-key") as client:
            assert isinstance(client, WikiJSClient)

        # Verify session was closed
        mock_session.close.assert_called_once()

    @patch("wikijs.client.requests.Session")
    def test_close_method(self, mock_session_class):
        """Test explicit close method."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        client = WikiJSClient("https://wiki.example.com", auth="test-key")
        client.close()

        mock_session.close.assert_called_once()

    @patch("wikijs.client.requests.Session")
    def test_repr(self, mock_session_class):
        """Test string representation."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        client = WikiJSClient("https://wiki.example.com", auth="test-key")
        repr_str = repr(client)

        assert "WikiJSClient" in repr_str
        assert "https://wiki.example.com" in repr_str

    @patch("wikijs.client.requests.Session")
    def test_connection_test_generic_exception(self, mock_session_class):
        """Test connection test with generic exception."""
        mock_session = Mock()
        mock_session_class.return_value = mock_session

        # Mock generic exception during connection test
        mock_session.request.side_effect = RuntimeError("Unexpected error")

        client = WikiJSClient("https://wiki.example.com", auth="test-key")

        from wikijs.exceptions import ConnectionError

        with pytest.raises(
            ConnectionError, match="Connection test failed: Unexpected error"
        ):
            client.test_connection()
