"""Main WikiJS client for wikijs-python-sdk."""

import json
from typing import Any, Dict, Optional, Union

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .auth import APIKeyAuth, AuthHandler
from .cache import BaseCache
from .endpoints import AssetsEndpoint, GroupsEndpoint, PagesEndpoint, UsersEndpoint
from .exceptions import (
    APIError,
    AuthenticationError,
    ConfigurationError,
    ConnectionError,
    TimeoutError,
    create_api_error,
)
from .utils import (
    build_api_url,
    extract_error_message,
    normalize_url,
    parse_wiki_response,
)
from .version import __version__


class WikiJSClient:
    """Main client for interacting with Wiki.js API.

    This client provides a high-level interface for all Wiki.js API operations
    including pages, users, groups, and system management. It handles authentication,
    error handling, and response parsing automatically.

    Args:
        base_url: The base URL of your Wiki.js instance
        auth: Authentication (API key string or auth handler)
        timeout: Request timeout in seconds (default: 30)
        verify_ssl: Whether to verify SSL certificates (default: True)
        user_agent: Custom User-Agent header
        cache: Optional cache instance for caching API responses

    Example:
        Basic usage with API key:

        >>> client = WikiJSClient('https://wiki.example.com', auth='your-api-key')
        >>> pages = client.pages.list()
        >>> page = client.pages.get(123)

        With caching enabled:

        >>> from wikijs.cache import MemoryCache
        >>> cache = MemoryCache(ttl=300)
        >>> client = WikiJSClient('https://wiki.example.com', auth='your-api-key', cache=cache)
        >>> page = client.pages.get(123)  # Fetches from API
        >>> page = client.pages.get(123)  # Returns from cache

    Attributes:
        base_url: The normalized base URL
        timeout: Request timeout setting
        verify_ssl: SSL verification setting
        cache: Optional cache instance
    """

    def __init__(
        self,
        base_url: str,
        auth: Union[str, AuthHandler],
        timeout: int = 30,
        verify_ssl: bool = True,
        user_agent: Optional[str] = None,
        cache: Optional[BaseCache] = None,
    ):
        # Instance variable declarations for mypy
        self._auth_handler: AuthHandler
        self._session: requests.Session

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

        # Cache configuration
        self.cache = cache

        # Initialize HTTP session
        self._session = self._create_session()

        # Endpoint handlers
        self.pages = PagesEndpoint(self)
        self.users = UsersEndpoint(self)
        self.groups = GroupsEndpoint(self)
        self.assets = AssetsEndpoint(self)

    def _create_session(self) -> requests.Session:
        """Create configured HTTP session with retry strategy.

        Returns:
            Configured requests session
        """
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=[
                "HEAD",
                "GET",
                "OPTIONS",
                "POST",
                "PUT",
                "DELETE",
            ],
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        # Set default headers
        session.headers.update(
            {
                "User-Agent": self.user_agent,
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
        )

        # Set authentication headers
        if self._auth_handler:
            # Validate auth and get headers
            self._auth_handler.validate_credentials()
            auth_headers = self._auth_handler.get_headers()
            session.headers.update(auth_headers)

        return session

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Make HTTP request to Wiki.js API.

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

        # Prepare request arguments
        request_kwargs = {
            "timeout": self.timeout,
            "verify": self.verify_ssl,
            "params": params,
            **kwargs,
        }

        # Add JSON data if provided
        if json_data is not None:
            request_kwargs["json"] = json_data

        try:
            # Make request
            response = self._session.request(method, url, **request_kwargs)

            # Handle response
            return self._handle_response(response)

        except requests.exceptions.Timeout as e:
            raise TimeoutError(f"Request timed out after {self.timeout} seconds") from e

        except requests.exceptions.ConnectionError as e:
            raise ConnectionError(f"Failed to connect to {self.base_url}") from e

        except requests.exceptions.RequestException as e:
            raise APIError(f"Request failed: {str(e)}") from e

    def _handle_response(self, response: requests.Response) -> Any:
        """Handle HTTP response and extract data.

        Args:
            response: HTTP response object

        Returns:
            Parsed response data

        Raises:
            AuthenticationError: If authentication fails (401)
            APIError: If API returns an error
        """
        # Handle authentication errors
        if response.status_code == 401:
            raise AuthenticationError("Authentication failed - check your API key")

        # Handle other HTTP errors
        if not response.ok:
            error_message = extract_error_message(response)
            raise create_api_error(response.status_code, error_message, response)

        # Parse JSON response
        try:
            data = response.json()
        except json.JSONDecodeError as e:
            raise APIError(f"Invalid JSON response: {str(e)}") from e

        # Parse Wiki.js specific response format
        return parse_wiki_response(data)

    def test_connection(self) -> bool:
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

            response = self._request("POST", "/graphql", json_data={"query": query})

            # Check for GraphQL errors
            if "errors" in response:
                error_msg = response["errors"][0].get("message", "Unknown error")
                raise AuthenticationError(
                    f"GraphQL query failed: {error_msg}"
                )

            # Verify we got expected data structure
            if "data" not in response or "site" not in response["data"]:
                raise APIError(
                    "Unexpected response format from Wiki.js API"
                )

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

    def __enter__(self) -> "WikiJSClient":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        """Context manager exit - close session."""
        self.close()

    def close(self) -> None:
        """Close the HTTP session and clean up resources."""
        if self._session:
            self._session.close()

    def __repr__(self) -> str:
        """String representation of client."""
        return f"WikiJSClient(base_url='{self.base_url}')"
