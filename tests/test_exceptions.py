"""Tests for exception classes."""

from unittest.mock import Mock

from wikijs.exceptions import (
    APIError,
    AuthenticationError,
    ClientError,
    ConfigurationError,
    ConnectionError,
    NotFoundError,
    PermissionError,
    RateLimitError,
    ServerError,
    TimeoutError,
    ValidationError,
    WikiJSException,
    create_api_error,
)


class TestWikiJSException:
    """Test base exception class."""

    def test_basic_exception_creation(self):
        """Test basic exception creation."""
        exc = WikiJSException("Test error")
        assert str(exc) == "Test error"
        assert exc.message == "Test error"

    def test_exception_with_details(self):
        """Test exception with details."""
        details = {"code": "TEST_ERROR", "field": "title"}
        exc = WikiJSException("Test error", details=details)
        assert exc.details == details


class TestAPIError:
    """Test API error classes."""

    def test_api_error_creation(self):
        """Test API error with status code and response."""
        response = Mock()
        response.status_code = 500
        response.text = "Internal server error"

        exc = APIError("Server error", status_code=500, response=response)
        assert exc.status_code == 500
        assert exc.response == response
        assert str(exc) == "Server error"


class TestRateLimitError:
    """Test rate limit error."""

    def test_rate_limit_error_with_retry_after(self):
        """Test rate limit error with retry_after parameter."""
        exc = RateLimitError("Rate limit exceeded", retry_after=60)
        assert exc.status_code == 429
        assert exc.retry_after == 60
        assert str(exc) == "Rate limit exceeded"

    def test_rate_limit_error_without_retry_after(self):
        """Test rate limit error without retry_after parameter."""
        exc = RateLimitError("Rate limit exceeded")
        assert exc.status_code == 429
        assert exc.retry_after is None


class TestCreateAPIError:
    """Test create_api_error factory function."""

    def test_create_404_error(self):
        """Test creating 404 NotFoundError."""
        response = Mock()
        error = create_api_error(404, "Not found", response)
        assert isinstance(error, NotFoundError)
        assert error.status_code == 404
        assert error.response == response

    def test_create_403_error(self):
        """Test creating 403 PermissionError."""
        response = Mock()
        error = create_api_error(403, "Forbidden", response)
        assert isinstance(error, PermissionError)
        assert error.status_code == 403

    def test_create_429_error(self):
        """Test creating 429 RateLimitError."""
        response = Mock()
        error = create_api_error(429, "Rate limited", response)
        assert isinstance(error, RateLimitError)
        assert error.status_code == 429
        # Note: RateLimitError constructor hardcodes status_code=429
        # so it doesn't use the passed status_code parameter

    def test_create_400_client_error(self):
        """Test creating generic 400-level ClientError."""
        response = Mock()
        error = create_api_error(400, "Bad request", response)
        assert isinstance(error, ClientError)
        assert error.status_code == 400

    def test_create_500_server_error(self):
        """Test creating generic 500-level ServerError."""
        response = Mock()
        error = create_api_error(500, "Server error", response)
        assert isinstance(error, ServerError)
        assert error.status_code == 500

    def test_create_unknown_status_error(self):
        """Test creating error with unknown status code."""
        response = Mock()
        error = create_api_error(999, "Unknown error", response)
        assert isinstance(error, APIError)
        assert error.status_code == 999


class TestSimpleExceptions:
    """Test simple exception classes."""

    def test_connection_error(self):
        """Test ConnectionError creation."""
        exc = ConnectionError("Connection failed")
        assert str(exc) == "Connection failed"
        assert isinstance(exc, WikiJSException)

    def test_timeout_error(self):
        """Test TimeoutError creation."""
        exc = TimeoutError("Request timed out")
        assert str(exc) == "Request timed out"
        assert isinstance(exc, WikiJSException)

    def test_authentication_error(self):
        """Test AuthenticationError creation."""
        exc = AuthenticationError("Invalid credentials")
        assert str(exc) == "Invalid credentials"
        assert isinstance(exc, WikiJSException)

    def test_configuration_error(self):
        """Test ConfigurationError creation."""
        exc = ConfigurationError("Invalid config")
        assert str(exc) == "Invalid config"
        assert isinstance(exc, WikiJSException)

    def test_validation_error(self):
        """Test ValidationError creation."""
        exc = ValidationError("Invalid input")
        assert str(exc) == "Invalid input"
        assert isinstance(exc, WikiJSException)
