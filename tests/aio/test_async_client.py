"""Tests for AsyncWikiJSClient."""

import json
from unittest.mock import AsyncMock, Mock, patch

import aiohttp
import pytest

from wikijs.aio import AsyncWikiJSClient
from wikijs.auth import APIKeyAuth
from wikijs.exceptions import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    ConnectionError,
    TimeoutError,
)


class TestAsyncWikiJSClientInit:
    """Test AsyncWikiJSClient initialization."""

    def test_init_with_api_key_string(self):
        """Test initialization with API key string."""
        client = AsyncWikiJSClient("https://wiki.example.com", auth="test-key")

        assert client.base_url == "https://wiki.example.com"
        assert isinstance(client._auth_handler, APIKeyAuth)
        assert client.timeout == 30
        assert client.verify_ssl is True
        assert "wikijs-python-sdk" in client.user_agent

    def test_init_with_auth_handler(self):
        """Test initialization with auth handler."""
        auth_handler = APIKeyAuth("test-key")
        client = AsyncWikiJSClient("https://wiki.example.com", auth=auth_handler)

        assert client._auth_handler is auth_handler

    def test_init_invalid_auth(self):
        """Test initialization with invalid auth parameter."""
        with pytest.raises(ConfigurationError, match="Invalid auth parameter"):
            AsyncWikiJSClient("https://wiki.example.com", auth=123)

    def test_init_with_custom_settings(self):
        """Test initialization with custom settings."""
        client = AsyncWikiJSClient(
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
        client = AsyncWikiJSClient("https://wiki.example.com", auth="test-key")

        assert hasattr(client, "pages")
        assert client.pages._client is client


class TestAsyncWikiJSClientRequest:
    """Test AsyncWikiJSClient HTTP request methods."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return AsyncWikiJSClient("https://wiki.example.com", auth="test-key")

    @pytest.mark.asyncio
    async def test_successful_request(self, client):
        """Test successful API request."""
        mock_response = AsyncMock()
        mock_response.status = 200
        # Response returns full data structure
        mock_response.json = AsyncMock(return_value={"data": {"result": "success"}})

        # Create a context manager mock
        mock_ctx_manager = AsyncMock()
        mock_ctx_manager.__aenter__.return_value = mock_response
        mock_ctx_manager.__aexit__.return_value = False

        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = Mock()
            mock_session.request = Mock(return_value=mock_ctx_manager)
            mock_get_session.return_value = mock_session

            result = await client._request("GET", "/test")

            # parse_wiki_response returns full response if no errors
            assert result == {"data": {"result": "success"}}
            mock_session.request.assert_called_once()

    @pytest.mark.asyncio
    async def test_authentication_error(self, client):
        """Test 401 authentication error."""
        mock_response = AsyncMock()
        mock_response.status = 401

        # Create a context manager mock
        mock_ctx_manager = AsyncMock()
        mock_ctx_manager.__aenter__.return_value = mock_response
        mock_ctx_manager.__aexit__.return_value = False

        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = Mock()
            mock_session.request = Mock(return_value=mock_ctx_manager)
            mock_get_session.return_value = mock_session

            with pytest.raises(AuthenticationError, match="Authentication failed"):
                await client._request("GET", "/test")

    @pytest.mark.asyncio
    async def test_api_error(self, client):
        """Test API error handling."""
        mock_response = AsyncMock()
        mock_response.status = 500
        mock_response.text = AsyncMock(return_value="Internal Server Error")

        # Create a context manager mock
        mock_ctx_manager = AsyncMock()
        mock_ctx_manager.__aenter__.return_value = mock_response
        mock_ctx_manager.__aexit__.return_value = False

        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = Mock()
            mock_session.request = Mock(return_value=mock_ctx_manager)
            mock_get_session.return_value = mock_session

            with pytest.raises(APIError):
                await client._request("GET", "/test")

    @pytest.mark.asyncio
    async def test_connection_error(self, client):
        """Test connection error handling."""
        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = Mock()
            mock_session.request = Mock(
                side_effect=aiohttp.ClientConnectionError("Connection failed")
            )
            mock_get_session.return_value = mock_session

            with pytest.raises(ConnectionError, match="Failed to connect"):
                await client._request("GET", "/test")

    @pytest.mark.asyncio
    async def test_timeout_error(self, client):
        """Test timeout error handling."""
        with patch.object(client, "_get_session") as mock_get_session:
            mock_session = Mock()
            mock_session.request = Mock(
                side_effect=aiohttp.ServerTimeoutError("Timeout")
            )
            mock_get_session.return_value = mock_session

            with pytest.raises(TimeoutError, match="timed out"):
                await client._request("GET", "/test")


class TestAsyncWikiJSClientTestConnection:
    """Test AsyncWikiJSClient connection testing."""

    @pytest.fixture
    def client(self):
        """Create test client."""
        return AsyncWikiJSClient("https://wiki.example.com", auth="test-key")

    @pytest.mark.asyncio
    async def test_successful_connection(self, client):
        """Test successful connection test."""
        mock_response = {"data": {"site": {"title": "Test Wiki"}}}

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            result = await client.test_connection()

            assert result is True
            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            assert args[0] == "POST"
            assert args[1] == "/graphql"
            assert "query" in kwargs["json_data"]

    @pytest.mark.asyncio
    async def test_connection_graphql_error(self, client):
        """Test connection with GraphQL error."""
        mock_response = {"errors": [{"message": "Unauthorized"}]}

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            with pytest.raises(AuthenticationError, match="GraphQL query failed"):
                await client.test_connection()

    @pytest.mark.asyncio
    async def test_connection_invalid_response(self, client):
        """Test connection with invalid response."""
        mock_response = {"data": {}}  # Missing 'site' key

        with patch.object(client, "_request", new_callable=AsyncMock) as mock_request:
            mock_request.return_value = mock_response

            with pytest.raises(APIError, match="Unexpected response format"):
                await client.test_connection()

    @pytest.mark.asyncio
    async def test_connection_no_base_url(self):
        """Test connection with no base URL."""
        client = AsyncWikiJSClient("https://wiki.example.com", auth="test-key")
        client.base_url = None

        with pytest.raises(ConfigurationError, match="Base URL not configured"):
            await client.test_connection()


class TestAsyncWikiJSClientContextManager:
    """Test AsyncWikiJSClient async context manager."""

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test async context manager."""
        client = AsyncWikiJSClient("https://wiki.example.com", auth="test-key")

        # Mock the session
        mock_session = AsyncMock()
        mock_session.closed = False

        with patch.object(client, "_create_session", return_value=mock_session):
            async with client as ctx_client:
                assert ctx_client is client
                assert client._session is mock_session

            # Check that close was called
            mock_session.close.assert_called_once()

    @pytest.mark.asyncio
    async def test_manual_close(self):
        """Test manual close."""
        client = AsyncWikiJSClient("https://wiki.example.com", auth="test-key")

        # Mock the session
        mock_session = AsyncMock()
        mock_session.closed = False
        client._session = mock_session

        await client.close()

        mock_session.close.assert_called_once()


class TestAsyncWikiJSClientSessionCreation:
    """Test AsyncWikiJSClient session creation."""

    @pytest.mark.asyncio
    async def test_create_session(self):
        """Test session creation."""
        client = AsyncWikiJSClient("https://wiki.example.com", auth="test-key")

        session = client._create_session()

        assert isinstance(session, aiohttp.ClientSession)
        assert "wikijs-python-sdk" in session.headers["User-Agent"]
        assert session.headers["Accept"] == "application/json"
        assert session.headers["Content-Type"] == "application/json"

        # Clean up
        await session.close()
        if client._connector:
            await client._connector.close()

    @pytest.mark.asyncio
    async def test_get_session_creates_if_none(self):
        """Test get_session creates session if none exists."""
        client = AsyncWikiJSClient("https://wiki.example.com", auth="test-key")

        assert client._session is None

        session = client._get_session()

        assert session is not None
        assert isinstance(session, aiohttp.ClientSession)

        # Clean up
        await session.close()
        if client._connector:
            await client._connector.close()

    @pytest.mark.asyncio
    async def test_get_session_reuses_existing(self):
        """Test get_session reuses existing session."""
        client = AsyncWikiJSClient("https://wiki.example.com", auth="test-key")

        session1 = client._get_session()
        session2 = client._get_session()

        assert session1 is session2

        # Clean up
        await session1.close()
        if client._connector:
            await client._connector.close()
