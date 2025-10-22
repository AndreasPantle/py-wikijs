"""Async WikiJS client for wikijs-python-sdk."""

import json
from typing import Any, Dict, Optional, Union

try:
    import aiohttp
except ImportError:
    raise ImportError(
        "aiohttp is required for async support. "
        "Install it with: pip install wikijs-python-sdk[async]"
    )

from ..auth import APIKeyAuth, AuthHandler
from ..exceptions import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    ConnectionError,
    TimeoutError,
    create_api_error,
)
from ..utils import (
    build_api_url,
    extract_error_message,
    normalize_url,
    parse_wiki_response,
)
from ..version import __version__
from .endpoints import AsyncAssetsEndpoint, AsyncGroupsEndpoint, AsyncPagesEndpoint, AsyncUsersEndpoint


class AsyncWikiJSClient:
    """Async client for interacting with Wiki.js API.

    This async client provides high-performance concurrent access to all Wiki.js
    API operations using aiohttp. It maintains the same interface as the sync
    client but with async/await support.

    Args:
        base_url: The base URL of your Wiki.js instance
        auth: Authentication (API key string or auth handler)
        timeout: Request timeout in seconds (default: 30)
        verify_ssl: Whether to verify SSL certificates (default: True)
        user_agent: Custom User-Agent header
        connector: Optional aiohttp connector for connection pooling

    Example:
        Basic async usage:

        >>> async with AsyncWikiJSClient('https://wiki.example.com', auth='key') as client:
        ...     pages = await client.pages.list()
        ...     page = await client.pages.get(123)

        Manual resource management:

        >>> client = AsyncWikiJSClient('https://wiki.example.com', auth='key')
        >>> try:
        ...     page = await client.pages.get(123)
        ... finally:
        ...     await client.close()

    Attributes:
        base_url: The normalized base URL
        timeout: Request timeout setting
        verify_ssl: SSL verification setting
    """

    def __init__(
        self,
        base_url: str,
        auth: Union[str, AuthHandler],
        timeout: int = 30,
        verify_ssl: bool = True,
        user_agent: Optional[str] = None,
        connector: Optional[aiohttp.BaseConnector] = None,
    ):
        # Instance variable declarations
        self._auth_handler: AuthHandler
        self._session: Optional[aiohttp.ClientSession] = None
        self._connector = connector
        self._owned_connector = connector is None

        # Validate and normalize base URL
        self.base_url = normalize_url(base_url)

        # Store authentication
        if isinstance(auth, str):
            # Convert string API key to APIKeyAuth handler
            self._auth_handler = APIKeyAuth(auth)
        elif isinstance(auth, AuthHandler):
            # Use provided auth handler
            self._auth_handler = auth
        else:
            raise ConfigurationError(
                f"Invalid auth parameter: expected str or AuthHandler, got {type(auth)}"
            )

        # Request configuration
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.user_agent = user_agent or f"wikijs-python-sdk/{__version__}"

        # Endpoint handlers (will be initialized when session is created)
        self.pages = AsyncPagesEndpoint(self)
        self.users = AsyncUsersEndpoint(self)
        self.groups = AsyncGroupsEndpoint(self)
        self.assets = AsyncAssetsEndpoint(self)

    def _get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session.

        Returns:
            Configured aiohttp session

        Raises:
            ConfigurationError: If session cannot be created
        """
        if self._session is None or self._session.closed:
            self._session = self._create_session()
        return self._session

    def _create_session(self) -> aiohttp.ClientSession:
        """Create configured aiohttp session with connection pooling.

        Returns:
            Configured aiohttp session
        """
        # Create connector if not provided
        if self._connector is None and self._owned_connector:
            self._connector = aiohttp.TCPConnector(
                limit=100,  # Maximum number of connections
                limit_per_host=30,  # Maximum per host
                ttl_dns_cache=300,  # DNS cache TTL
                ssl=self.verify_ssl,
            )

        # Set timeout
        timeout_obj = aiohttp.ClientTimeout(total=self.timeout)

        # Build headers
        headers = {
            "User-Agent": self.user_agent,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        # Add authentication headers
        if self._auth_handler:
            self._auth_handler.validate_credentials()
            auth_headers = self._auth_handler.get_headers()
            headers.update(auth_headers)

        # Create session
        session = aiohttp.ClientSession(
            connector=self._connector,
            timeout=timeout_obj,
            headers=headers,
            raise_for_status=False,  # We'll handle status codes manually
        )

        return session

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Make async HTTP request to Wiki.js API.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            params: Query parameters
            json_data: JSON data for request body
            **kwargs: Additional request parameters

        Returns:
            Parsed response data

        Raises:
            AuthenticationError: If authentication fails
            APIError: If API returns an error
            ConnectionError: If connection fails
            TimeoutError: If request times out
        """
        # Build full URL
        url = build_api_url(self.base_url, endpoint)

        # Get session
        session = self._get_session()

        # Prepare request arguments
        request_kwargs: Dict[str, Any] = {
            "params": params,
            "ssl": self.verify_ssl,
            **kwargs,
        }

        # Add JSON data if provided
        if json_data is not None:
            request_kwargs["json"] = json_data

        try:
            # Make async request
            async with session.request(method, url, **request_kwargs) as response:
                # Handle response
                return await self._handle_response(response)

        except aiohttp.ServerTimeoutError as e:
            raise TimeoutError(f"Request timed out after {self.timeout} seconds") from e

        except asyncio.TimeoutError as e:
            raise TimeoutError(f"Request timed out after {self.timeout} seconds") from e

        except aiohttp.ClientConnectionError as e:
            raise ConnectionError(f"Failed to connect to {self.base_url}") from e

        except aiohttp.ClientError as e:
            raise APIError(f"Request failed: {str(e)}") from e

    async def _handle_response(self, response: aiohttp.ClientResponse) -> Any:
        """Handle async HTTP response and extract data.

        Args:
            response: aiohttp response object

        Returns:
            Parsed response data

        Raises:
            AuthenticationError: If authentication fails (401)
            APIError: If API returns an error
        """
        # Handle authentication errors
        if response.status == 401:
            raise AuthenticationError("Authentication failed - check your API key")

        # Handle other HTTP errors
        if response.status >= 400:
            # Try to read response text for error message
            try:
                response_text = await response.text()

                # Create a mock response object for extract_error_message
                class MockResponse:
                    def __init__(self, status, text):
                        self.status_code = status
                        self.text = text
                        try:
                            self._json = json.loads(text) if text else {}
                        except json.JSONDecodeError:
                            self._json = {}

                    def json(self):
                        return self._json

                mock_resp = MockResponse(response.status, response_text)
                error_message = extract_error_message(mock_resp)
            except Exception:
                error_message = f"HTTP {response.status}"

            raise create_api_error(response.status, error_message, None)

        # Parse JSON response
        try:
            data = await response.json()
        except json.JSONDecodeError as e:
            response_text = await response.text()
            raise APIError(
                f"Invalid JSON response: {str(e)}. Response: {response_text[:200]}"
            ) from e

        # Parse Wiki.js specific response format
        return parse_wiki_response(data)

    async def test_connection(self) -> bool:
        """Test connection to Wiki.js instance.

        This method validates the connection by making an actual GraphQL query
        to the Wiki.js API, ensuring both connectivity and authentication work.

        Returns:
            True if connection successful

        Raises:
            ConfigurationError: If client is not properly configured
            ConnectionError: If cannot connect to server
            AuthenticationError: If authentication fails
            TimeoutError: If connection test times out
        """
        if not self.base_url:
            raise ConfigurationError("Base URL not configured")

        if not self._auth_handler:
            raise ConfigurationError("Authentication not configured")

        try:
            # Test with minimal GraphQL query to validate API access
            query = """
            query {
                site {
                    title
                }
            }
            """

            response = await self._request(
                "POST", "/graphql", json_data={"query": query}
            )

            # Check for GraphQL errors
            if "errors" in response:
                error_msg = response["errors"][0].get("message", "Unknown error")
                raise AuthenticationError(f"GraphQL query failed: {error_msg}")

            # Verify we got expected data structure
            if "data" not in response or "site" not in response["data"]:
                raise APIError("Unexpected response format from Wiki.js API")

            return True

        except AuthenticationError:
            # Re-raise authentication errors as-is
            raise

        except TimeoutError:
            # Re-raise timeout errors as-is
            raise

        except ConnectionError:
            # Re-raise connection errors as-is
            raise

        except APIError:
            # Re-raise API errors as-is
            raise

        except Exception as e:
            raise ConnectionError(f"Connection test failed: {str(e)}")

    async def __aenter__(self) -> "AsyncWikiJSClient":
        """Async context manager entry."""
        # Ensure session is created
        self._get_session()
        return self

    async def __aexit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Async context manager exit - close session."""
        await self.close()

    async def close(self) -> None:
        """Close the aiohttp session and clean up resources."""
        if self._session and not self._session.closed:
            await self._session.close()

        # Close connector if we own it
        if self._owned_connector and self._connector and not self._connector.closed:
            await self._connector.close()

    def __repr__(self) -> str:
        """String representation of client."""
        return f"AsyncWikiJSClient(base_url='{self.base_url}')"


# Need to import asyncio for timeout handling
import asyncio  # noqa: E402
