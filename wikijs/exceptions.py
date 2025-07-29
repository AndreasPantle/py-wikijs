"""Exception hierarchy for wikijs-python-sdk."""

from typing import Any, Dict, Optional


class WikiJSException(Exception):
    """Base exception for all SDK errors."""
    
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class ConfigurationError(WikiJSException):
    """Raised when there's an issue with SDK configuration."""
    pass


class AuthenticationError(WikiJSException):
    """Raised when authentication fails."""
    pass


class ValidationError(WikiJSException):
    """Raised when input validation fails."""
    
    def __init__(self, message: str, field: Optional[str] = None, value: Any = None):
        super().__init__(message)
        self.field = field
        self.value = value


class APIError(WikiJSException):
    """Base class for API-related errors."""
    
    def __init__(
        self, 
        message: str, 
        status_code: Optional[int] = None, 
        response: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, details)
        self.status_code = status_code
        self.response = response


class ClientError(APIError):
    """Raised for 4xx HTTP status codes (client errors)."""
    pass


class ServerError(APIError):
    """Raised for 5xx HTTP status codes (server errors)."""
    pass


class NotFoundError(ClientError):
    """Raised when a requested resource is not found (404)."""
    pass


class PermissionError(ClientError):
    """Raised when access is forbidden (403)."""
    pass


class RateLimitError(ClientError):
    """Raised when rate limit is exceeded (429)."""
    
    def __init__(self, message: str, retry_after: Optional[int] = None, **kwargs):
        super().__init__(message, status_code=429, **kwargs)
        self.retry_after = retry_after


class ConnectionError(WikiJSException):
    """Raised when there's a connection issue."""
    pass


class TimeoutError(WikiJSException):
    """Raised when a request times out."""
    pass


def create_api_error(status_code: int, message: str, response: Any = None) -> APIError:
    """Create appropriate API error based on status code.
    
    Args:
        status_code: HTTP status code
        message: Error message
        response: Raw response object
    
    Returns:
        Appropriate APIError subclass instance
    """
    if status_code == 404:
        return NotFoundError(message, status_code=status_code, response=response)
    elif status_code == 403:
        return PermissionError(message, status_code=status_code, response=response)
    elif status_code == 429:
        return RateLimitError(message, status_code=status_code, response=response)
    elif 400 <= status_code < 500:
        return ClientError(message, status_code=status_code, response=response)
    elif 500 <= status_code < 600:
        return ServerError(message, status_code=status_code, response=response)
    else:
        return APIError(message, status_code=status_code, response=response)