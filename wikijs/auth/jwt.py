"""JWT token authentication for wikijs-python-sdk.

This module implements JWT (JSON Web Token) authentication for Wiki.js instances.
JWT tokens are typically used for user-based authentication and have expiration times.
"""

import time
from datetime import timedelta
from typing import Dict, Optional

from .base import AuthHandler


class JWTAuth(AuthHandler):
    """JWT token authentication handler for Wiki.js.

    This handler manages JWT tokens with automatic refresh capabilities.
    JWT tokens typically expire and need to be refreshed periodically.

    Args:
        token: The JWT token string.
        refresh_token: Optional refresh token for automatic renewal.
        expires_at: Optional expiration timestamp (Unix timestamp).

    Example:
        >>> auth = JWTAuth("eyJ0eXAiOiJKV1QiLCJhbGc...")
        >>> client = WikiJSClient("https://wiki.example.com", auth=auth)
    """

    def __init__(
        self,
        token: str,
        refresh_token: Optional[str] = None,
        expires_at: Optional[float] = None,
    ) -> None:
        """Initialize JWT authentication.

        Args:
            token: The JWT token string.
            refresh_token: Optional refresh token for automatic renewal.
            expires_at: Optional expiration timestamp (Unix timestamp).

        Raises:
            ValueError: If token is empty or None.
        """
        if not token or not token.strip():
            raise ValueError("JWT token cannot be empty")

        self._token = token.strip()
        self._refresh_token = refresh_token.strip() if refresh_token else None
        self._expires_at = expires_at
        self._refresh_buffer = 300  # Refresh 5 minutes before expiration

    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers with JWT token.

        Automatically attempts to refresh the token if it's expired.

        Returns:
            Dict[str, str]: Headers containing the Authorization header.

        Raises:
            AuthenticationError: If token is expired and cannot be refreshed.
        """
        # Try to refresh if token is near expiration
        if not self.is_valid():
            self.refresh()

        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json",
        }

    def is_valid(self) -> bool:
        """Check if JWT token is valid and not expired.

        Returns:
            bool: True if token exists and is not expired, False otherwise.
        """
        if not self._token or not self._token.strip():
            return False

        # If no expiration time is set, assume token is valid
        if self._expires_at is None:
            return True

        # Check if token is expired (with buffer for refresh)
        current_time = time.time()
        return current_time < (self._expires_at - self._refresh_buffer)

    def refresh(self) -> None:
        """Refresh the JWT token using the refresh token.

        This method attempts to refresh the JWT token using the refresh token.
        If no refresh token is available, it raises an AuthenticationError.

        Note: This is a placeholder implementation. In a real implementation,
        this would make an HTTP request to the Wiki.js token refresh endpoint.

        Raises:
            AuthenticationError: If refresh token is not available or refresh fails.
        """
        from ..exceptions import AuthenticationError

        if not self._refresh_token:
            raise AuthenticationError(
                "JWT token expired and no refresh token available"
            )

        # TODO: Implement actual token refresh logic
        # This would typically involve:
        # 1. Making a POST request to /auth/refresh endpoint
        # 2. Sending the refresh token
        # 3. Updating self._token and self._expires_at with the response

        raise AuthenticationError(
            "JWT token refresh not yet implemented. "
            "Please provide a new token or use API key authentication."
        )

    def is_expired(self) -> bool:
        """Check if the JWT token is expired.

        Returns:
            bool: True if token is expired, False otherwise.
        """
        if self._expires_at is None:
            return False

        return time.time() >= self._expires_at

    def time_until_expiry(self) -> Optional[timedelta]:
        """Get time until token expires.

        Returns:
            Optional[timedelta]: Time until expiration, or None if no expiration set.
        """
        if self._expires_at is None:
            return None

        remaining_seconds = self._expires_at - time.time()
        return timedelta(seconds=max(0, remaining_seconds))

    @property
    def token_preview(self) -> str:
        """Get a preview of the JWT token for logging/debugging.

        Returns:
            str: Masked token showing only first and last few characters.
        """
        if not self._token:
            return "None"

        if len(self._token) <= 20:
            return "*" * len(self._token)

        return f"{self._token[:10]}...{self._token[-10:]}"

    def __repr__(self) -> str:
        """String representation of the auth handler.

        Returns:
            str: Safe representation with masked token.
        """
        return f"JWTAuth(token='{self.token_preview}', expires_at={self._expires_at})"
