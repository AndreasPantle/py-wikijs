"""Base endpoint class for py-wikijs."""

from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from ..client import WikiJSClient


class BaseEndpoint:
    """Base class for all API endpoints.

    This class provides common functionality for making API requests
    and handling responses across all endpoint implementations.

    Args:
        client: The WikiJS client instance
    """

    def __init__(self, client: "WikiJSClient"):
        """Initialize endpoint with client reference.

        Args:
            client: WikiJS client instance
        """
        self._client = client

    def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Make HTTP request through the client.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            params: Query parameters
            json_data: JSON data for request body
            **kwargs: Additional request parameters

        Returns:
            Parsed response data
        """
        return self._client._request(
            method=method,
            endpoint=endpoint,
            params=params,
            json_data=json_data,
            **kwargs,
        )

    def _get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Any:
        """Make GET request.

        Args:
            endpoint: API endpoint path
            params: Query parameters
            **kwargs: Additional request parameters

        Returns:
            Parsed response data
        """
        return self._request("GET", endpoint, params=params, **kwargs)

    def _post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Make POST request.

        Args:
            endpoint: API endpoint path
            json_data: JSON data for request body
            params: Query parameters
            **kwargs: Additional request parameters

        Returns:
            Parsed response data
        """
        return self._request(
            "POST", endpoint, params=params, json_data=json_data, **kwargs
        )

    def _put(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Make PUT request.

        Args:
            endpoint: API endpoint path
            json_data: JSON data for request body
            params: Query parameters
            **kwargs: Additional request parameters

        Returns:
            Parsed response data
        """
        return self._request(
            "PUT", endpoint, params=params, json_data=json_data, **kwargs
        )

    def _delete(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Any:
        """Make DELETE request.

        Args:
            endpoint: API endpoint path
            params: Query parameters
            **kwargs: Additional request parameters

        Returns:
            Parsed response data
        """
        return self._request("DELETE", endpoint, params=params, **kwargs)

    def _build_endpoint(self, *parts: str) -> str:
        """Build endpoint path from parts.

        Args:
            *parts: Path components

        Returns:
            Formatted endpoint path
        """
        # Remove empty parts and join with /
        clean_parts = [str(part).strip("/") for part in parts if part]
        return "/" + "/".join(clean_parts)
