"""Tests for base authentication functionality."""

import pytest

from wikijs.auth.base import AuthHandler, NoAuth
from wikijs.exceptions import AuthenticationError


class TestAuthHandler:
    """Test abstract AuthHandler functionality."""

    def test_cannot_instantiate_abstract_class(self):
        """Test that AuthHandler cannot be instantiated directly."""
        with pytest.raises(TypeError):
            AuthHandler()

    def test_validate_credentials_calls_is_valid(self):
        """Test that validate_credentials calls is_valid."""

        # Create concrete implementation for testing
        class TestAuth(AuthHandler):
            def __init__(self, valid=True):
                self.valid = valid
                self.refresh_called = False

            def get_headers(self):
                return {"Authorization": "test"}

            def is_valid(self):
                return self.valid

            def refresh(self):
                self.refresh_called = True
                self.valid = True

        # Test valid credentials
        auth = TestAuth(valid=True)
        auth.validate_credentials()  # Should not raise
        assert not auth.refresh_called

        # Test invalid credentials that can be refreshed
        auth = TestAuth(valid=False)
        auth.validate_credentials()  # Should not raise
        assert auth.refresh_called
        assert auth.valid

    def test_validate_credentials_raises_on_invalid_after_refresh(self):
        """Test that validate_credentials raises if still invalid after refresh."""

        class TestAuth(AuthHandler):
            def get_headers(self):
                return {"Authorization": "test"}

            def is_valid(self):
                return False  # Always invalid

            def refresh(self):
                pass  # No-op refresh

        auth = TestAuth()
        with pytest.raises(
            AuthenticationError, match="Authentication credentials are invalid"
        ):
            auth.validate_credentials()


class TestNoAuth:
    """Test NoAuth implementation."""

    def test_init(self, no_auth):
        """Test NoAuth initialization."""
        assert isinstance(no_auth, NoAuth)

    def test_get_headers_returns_empty_dict(self, no_auth):
        """Test that get_headers returns empty dictionary."""
        headers = no_auth.get_headers()
        assert headers == {}
        assert isinstance(headers, dict)

    def test_is_valid_always_true(self, no_auth):
        """Test that is_valid always returns True."""
        assert no_auth.is_valid() is True

    def test_refresh_is_noop(self, no_auth):
        """Test that refresh does nothing."""
        # Should not raise any exception
        no_auth.refresh()
        # State should be unchanged
        assert no_auth.is_valid() is True

    def test_validate_credentials_succeeds(self, no_auth):
        """Test that validate_credentials always succeeds."""
        # Should not raise any exception
        no_auth.validate_credentials()
        assert no_auth.is_valid() is True
