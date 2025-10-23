"""Tests for JWT authentication."""

import time
from datetime import timedelta
from unittest.mock import patch

import pytest

from wikijs.auth.jwt import JWTAuth
from wikijs.exceptions import AuthenticationError


class TestJWTAuth:
    """Test JWTAuth implementation."""

    def test_init_with_valid_token(self, mock_jwt_token, mock_wiki_base_url):
        """Test initialization with valid JWT token."""
        auth = JWTAuth(mock_jwt_token, mock_wiki_base_url)
        assert auth._token == mock_jwt_token
        assert auth._base_url == mock_wiki_base_url
        assert auth._refresh_token is None
        assert auth._expires_at is None

    def test_init_with_all_parameters(self, mock_jwt_token, mock_wiki_base_url):
        """Test initialization with all parameters."""
        refresh_token = "refresh-token-123"
        expires_at = time.time() + 3600

        auth = JWTAuth(mock_jwt_token, mock_wiki_base_url, refresh_token, expires_at)
        assert auth._token == mock_jwt_token
        assert auth._base_url == mock_wiki_base_url
        assert auth._refresh_token == refresh_token
        assert auth._expires_at == expires_at

    def test_init_with_whitespace_token(self, mock_wiki_base_url):
        """Test initialization trims whitespace from token."""
        auth = JWTAuth("  test-token  ", mock_wiki_base_url)
        assert auth._token == "test-token"

    def test_init_with_empty_token_raises_error(self, mock_wiki_base_url):
        """Test that empty JWT token raises ValueError."""
        with pytest.raises(ValueError, match="JWT token cannot be empty"):
            JWTAuth("", mock_wiki_base_url)

    def test_init_with_whitespace_only_token_raises_error(self, mock_wiki_base_url):
        """Test that whitespace-only JWT token raises ValueError."""
        with pytest.raises(ValueError, match="JWT token cannot be empty"):
            JWTAuth("   ", mock_wiki_base_url)

    def test_init_with_none_raises_error(self, mock_wiki_base_url):
        """Test that None JWT token raises ValueError."""
        with pytest.raises(ValueError, match="JWT token cannot be empty"):
            JWTAuth(None, mock_wiki_base_url)

    def test_init_with_empty_base_url_raises_error(self, mock_jwt_token):
        """Test that empty base URL raises ValueError."""
        with pytest.raises(ValueError, match="Base URL cannot be empty"):
            JWTAuth(mock_jwt_token, "")

    def test_init_with_whitespace_base_url_raises_error(self, mock_jwt_token):
        """Test that whitespace-only base URL raises ValueError."""
        with pytest.raises(ValueError, match="Base URL cannot be empty"):
            JWTAuth(mock_jwt_token, "   ")

    def test_get_headers_returns_bearer_token(self, jwt_auth, mock_jwt_token):
        """Test that get_headers returns proper Authorization header."""
        headers = jwt_auth.get_headers()

        expected_headers = {
            "Authorization": f"Bearer {mock_jwt_token}",
            "Content-Type": "application/json",
        }
        assert headers == expected_headers

    def test_get_headers_attempts_refresh_if_invalid(self, mock_jwt_token, mock_wiki_base_url):
        """Test that get_headers attempts refresh if token is invalid."""
        # Create JWT with expired token
        expires_at = time.time() - 3600  # Expired 1 hour ago
        refresh_token = "refresh-token-123"

        auth = JWTAuth(mock_jwt_token, mock_wiki_base_url, refresh_token, expires_at)

        # Mock the refresh method to avoid actual implementation
        with patch.object(auth, "refresh") as mock_refresh:
            mock_refresh.side_effect = AuthenticationError("Refresh failed")

            with pytest.raises(AuthenticationError):
                auth.get_headers()

            mock_refresh.assert_called_once()

    def test_is_valid_returns_true_for_valid_token_no_expiry(self, jwt_auth):
        """Test that is_valid returns True for valid token without expiry."""
        assert jwt_auth.is_valid() is True

    def test_is_valid_returns_true_for_non_expired_token(self, mock_jwt_token, mock_wiki_base_url):
        """Test that is_valid returns True for non-expired token."""
        expires_at = time.time() + 3600  # Expires in 1 hour
        auth = JWTAuth(mock_jwt_token, mock_wiki_base_url, expires_at=expires_at)
        assert auth.is_valid() is True

    def test_is_valid_returns_false_for_expired_token(self, mock_jwt_token, mock_wiki_base_url):
        """Test that is_valid returns False for expired token."""
        expires_at = time.time() - 3600  # Expired 1 hour ago
        auth = JWTAuth(mock_jwt_token, mock_wiki_base_url, expires_at=expires_at)
        assert auth.is_valid() is False

    def test_is_valid_considers_refresh_buffer(self, mock_jwt_token, mock_wiki_base_url):
        """Test that is_valid considers refresh buffer."""
        # Token expires in 4 minutes (less than 5 minute buffer)
        expires_at = time.time() + 240
        auth = JWTAuth(mock_jwt_token, mock_wiki_base_url, expires_at=expires_at)
        assert auth.is_valid() is False  # Should be invalid due to buffer

    def test_is_valid_returns_false_for_empty_token(self, mock_jwt_token, mock_wiki_base_url):
        """Test that is_valid handles edge cases."""
        auth = JWTAuth(mock_jwt_token, mock_wiki_base_url)
        auth._token = ""
        assert auth.is_valid() is False

        auth._token = None
        assert auth.is_valid() is False

    def test_refresh_raises_error_without_refresh_token(self, jwt_auth):
        """Test that refresh raises error when no refresh token available."""
        with pytest.raises(
            AuthenticationError,
            match="JWT token expired and no refresh token available",
        ):
            jwt_auth.refresh()

    def test_refresh_with_refresh_token(self, mock_jwt_token, mock_wiki_base_url):
        """Test that refresh is now implemented with refresh token."""
        refresh_token = "refresh-token-123"
        auth = JWTAuth(mock_jwt_token, mock_wiki_base_url, refresh_token)

        # Mock the requests.post call
        with patch("requests.post") as mock_post:
            # Simulate failed refresh (network issue)
            mock_post.side_effect = Exception("Network error")

            with pytest.raises(AuthenticationError, match="Unexpected error during token refresh"):
                auth.refresh()

    def test_is_expired_returns_false_no_expiry(self, jwt_auth):
        """Test that is_expired returns False when no expiry set."""
        assert jwt_auth.is_expired() is False

    def test_is_expired_returns_false_for_valid_token(self, mock_jwt_token, mock_wiki_base_url):
        """Test that is_expired returns False for valid token."""
        expires_at = time.time() + 3600  # Expires in 1 hour
        auth = JWTAuth(mock_jwt_token, mock_wiki_base_url, expires_at=expires_at)
        assert auth.is_expired() is False

    def test_is_expired_returns_true_for_expired_token(self, mock_jwt_token, mock_wiki_base_url):
        """Test that is_expired returns True for expired token."""
        expires_at = time.time() - 3600  # Expired 1 hour ago
        auth = JWTAuth(mock_jwt_token, mock_wiki_base_url, expires_at=expires_at)
        assert auth.is_expired() is True

    def test_time_until_expiry_returns_none_no_expiry(self, jwt_auth):
        """Test that time_until_expiry returns None when no expiry set."""
        assert jwt_auth.time_until_expiry() is None

    def test_time_until_expiry_returns_correct_delta(self, mock_jwt_token, mock_wiki_base_url):
        """Test that time_until_expiry returns correct timedelta."""
        expires_at = time.time() + 3600  # Expires in 1 hour
        auth = JWTAuth(mock_jwt_token, mock_wiki_base_url, expires_at=expires_at)

        time_left = auth.time_until_expiry()
        assert isinstance(time_left, timedelta)
        # Should be approximately 1 hour (allowing for small time differences)
        assert 3550 <= time_left.total_seconds() <= 3600

    def test_time_until_expiry_returns_zero_for_expired(self, mock_jwt_token, mock_wiki_base_url):
        """Test that time_until_expiry returns zero for expired token."""
        expires_at = time.time() - 3600  # Expired 1 hour ago
        auth = JWTAuth(mock_jwt_token, mock_wiki_base_url, expires_at=expires_at)

        time_left = auth.time_until_expiry()
        assert time_left.total_seconds() == 0

    def test_token_preview_masks_token(self, mock_jwt_token, mock_wiki_base_url):
        """Test that token_preview masks the token for security."""
        auth = JWTAuth(mock_jwt_token, mock_wiki_base_url)
        preview = auth.token_preview

        assert preview != mock_jwt_token  # Should not show full token
        assert preview.startswith(mock_jwt_token[:10])
        assert preview.endswith(mock_jwt_token[-10:])
        assert "..." in preview

    def test_token_preview_handles_short_token(self, mock_wiki_base_url):
        """Test that token_preview handles short tokens."""
        short_token = "short"
        auth = JWTAuth(short_token, mock_wiki_base_url)
        preview = auth.token_preview

        assert preview == "*****"  # Should be all asterisks

    def test_token_preview_handles_none_token(self, mock_jwt_token, mock_wiki_base_url):
        """Test that token_preview handles None token."""
        auth = JWTAuth(mock_jwt_token, mock_wiki_base_url)
        auth._token = None

        assert auth.token_preview == "None"

    def test_repr_shows_masked_token(self, mock_jwt_token, mock_wiki_base_url):
        """Test that __repr__ shows masked token."""
        expires_at = time.time() + 3600
        auth = JWTAuth(mock_jwt_token, mock_wiki_base_url, expires_at=expires_at)
        repr_str = repr(auth)

        assert "JWTAuth" in repr_str
        assert mock_jwt_token not in repr_str  # Real token should not appear
        assert auth.token_preview in repr_str  # Masked token should appear
        assert str(expires_at) in repr_str

    def test_validate_credentials_succeeds_for_valid_token(self, jwt_auth):
        """Test that validate_credentials succeeds for valid token."""
        # Should not raise any exception
        jwt_auth.validate_credentials()
        assert jwt_auth.is_valid() is True

    def test_refresh_token_whitespace_handling(self, mock_jwt_token, mock_wiki_base_url):
        """Test that refresh token whitespace is handled correctly."""
        refresh_token = "  refresh-token-123  "
        auth = JWTAuth(mock_jwt_token, mock_wiki_base_url, refresh_token)
        assert auth._refresh_token == "refresh-token-123"

        # Test None refresh token
        auth = JWTAuth(mock_jwt_token, mock_wiki_base_url, None)
        assert auth._refresh_token is None
