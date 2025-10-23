"""Base authentication interface for py-wikijs.

This module defines the abstract base class for all authentication handlers,
providing a consistent interface for different authentication methods.
"""

from abc import ABC, abstractmethod
from typing import Dict


class AuthHandler(ABC):
    """Abstract base class for Wiki.js authentication handlers.

    This class defines the interface that all authentication implementations
    must follow, ensuring consistent behavior across different auth methods.
    """

    @abstractmethod
    def get_headers(self) -> Dict[str, str]:
        """Get authentication headers for HTTP requests.

        Returns:
            Dict[str, str]: Dictionary of headers to include in requests.

        Raises:
            AuthenticationError: If authentication is invalid or expired.
        """

    @abstractmethod
    def is_valid(self) -> bool:
        """Check if the current authentication is valid.

        Returns:
            bool: True if authentication is valid, False otherwise.
        """

    @abstractmethod
    def refresh(self) -> None:
        """Refresh the authentication if possible.

        For token-based authentication, this should refresh the token.
        For API key authentication, this is typically a no-op.

        Raises:
            AuthenticationError: If refresh fails.
        """

    def validate_credentials(self) -> None:
        """Validate credentials and refresh if necessary.

        This is a convenience method that checks validity and refreshes
        if needed. Subclasses can override for custom behavior.

        Raises:
            AuthenticationError: If credentials are invalid or refresh fails.
        """
        if not self.is_valid():
            self.refresh()

        if not self.is_valid():
            from ..exceptions import AuthenticationError

            raise AuthenticationError("Authentication credentials are invalid")


class NoAuth(AuthHandler):
    """No-authentication handler for testing or public instances.

    This handler provides an empty authentication implementation,
    useful for testing or when accessing public Wiki.js instances
    that don't require authentication.
    """

    def get_headers(self) -> Dict[str, str]:
        """Return empty headers dict.

        Returns:
            Dict[str, str]: Empty dictionary.
        """
        return {}

    def is_valid(self) -> bool:
        """Always return True for no-auth.

        Returns:
            bool: Always True.
        """
        return True

    def refresh(self) -> None:
        """No-op for no-auth.

        This method does nothing since there's no authentication to refresh.
        """
