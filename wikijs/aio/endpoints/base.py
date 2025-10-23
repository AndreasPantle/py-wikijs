"""Base async endpoint class for py-wikijs."""

from typing import TYPE_CHECKING, Any, Dict, Optional

if TYPE_CHECKING:
    from ..client import AsyncWikiJSClient


class AsyncBaseEndpoint:
    """Base class for all async API endpoints.

    This class provides common functionality for making async API requests
    and handling responses across all endpoint implementations.

    Args:
        client: The async WikiJS client instance
    """

    def __init__(self, client: "AsyncWikiJSClient"):
        """Initialize endpoint with client reference.

        Args:
            client: Async WikiJS client instance
        """
        self._client = client

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        json_data: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Make async HTTP request through the client.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            params: Query parameters
            json_data: JSON data for request body
            **kwargs: Additional request parameters

        Returns:
            Parsed response data
        """
        return await self._client._request(
            method=method,
            endpoint=endpoint,
            params=params,
            json_data=json_data,
            **kwargs,
        )

    async def _get(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Any:
        """Make async GET request.

        Args:
            endpoint: API endpoint path
            params: Query parameters
            **kwargs: Additional request parameters

        Returns:
            Parsed response data
        """
        return await self._request("GET", endpoint, params=params, **kwargs)

    async def _post(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Make async POST request.

        Args:
            endpoint: API endpoint path
            json_data: JSON data for request body
            params: Query parameters
            **kwargs: Additional request parameters

        Returns:
            Parsed response data
        """
        return await self._request(
            "POST", endpoint, params=params, json_data=json_data, **kwargs
        )

    async def _put(
        self,
        endpoint: str,
        json_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        **kwargs: Any,
    ) -> Any:
        """Make async PUT request.

        Args:
            endpoint: API endpoint path
            json_data: JSON data for request body
            params: Query parameters
            **kwargs: Additional request parameters

        Returns:
            Parsed response data
        """
        return await self._request(
            "PUT", endpoint, params=params, json_data=json_data, **kwargs
        )

    async def _delete(
        self, endpoint: str, params: Optional[Dict[str, Any]] = None, **kwargs: Any
    ) -> Any:
        """Make async DELETE request.

        Args:
            endpoint: API endpoint path
            params: Query parameters
            **kwargs: Additional request parameters

        Returns:
            Parsed response data
        """
        return await self._request("DELETE", endpoint, params=params, **kwargs)

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
