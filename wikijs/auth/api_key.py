"""API key authentication for py-wikijs.

This module implements API key authentication for Wiki.js instances.
API keys are typically used for server-to-server authentication.
"""

from typing import Dict

from .base import AuthHandler


class APIKeyAuth(AuthHandler):
    """API key authentication handler for Wiki.js.

    This handler implements authentication using an API key, which is
    included in the Authorization header as a Bearer token.

    Args:
        api_key: The API key string from Wiki.js admin panel.

    Example:
        >>> auth = APIKeyAuth("your-api-key-here")
        >>> client = WikiJSClient("https://wiki.example.com", auth=auth)
    """

    def __init__(self, api_key: str) -> None:
        """Initialize API key authentication.

        Args:
            api_key: The API key from Wiki.js admin panel.

        Raises:
            ValueError: If api_key is empty or None.
        """
        if not api_key or not api_key.strip():
            raise ValueError("API key cannot be empty")

        self._api_key = api_key.strip()

    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers with API key.

        Returns:
            Dict[str, str]: Headers containing the Authorization header.
        """
        return {
            "Authorization": f"Bearer {self._api_key}",
            "Content-Type": "application/json",
        }

    def is_valid(self) -> bool:
        """Check if API key is valid.

        For API keys, we assume they're valid if they're not empty.
        Actual validation happens on the server side.

        Returns:
            bool: True if API key exists, False otherwise.
        """
        return bool(self._api_key and self._api_key.strip())

    def refresh(self) -> None:
        """Refresh authentication credentials.

        API keys don't typically need refreshing, so this is a no-op.
        If the API key becomes invalid, a new one must be provided.
        """
        # API keys don't refresh - they're static until manually replaced

    @property
    def api_key(self) -> str:
        """Get the masked API key for logging/debugging.

        Returns:
            str: Masked API key showing only first 4 and last 4 characters.
        """
        if len(self._api_key) <= 8:
            return "*" * len(self._api_key)

        return (
            f"{self._api_key[:4]}{'*' * (len(self._api_key) - 8)}{self._api_key[-4:]}"
        )

    def __repr__(self) -> str:
        """String representation of the auth handler.

        Returns:
            str: Safe representation with masked API key.
        """
        return f"APIKeyAuth(api_key='{self.api_key}')"
