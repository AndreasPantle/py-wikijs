"""Tests for API key authentication."""

import pytest

from wikijs.auth.api_key import APIKeyAuth


class TestAPIKeyAuth:
    """Test APIKeyAuth implementation."""

    def test_init_with_valid_key(self, mock_api_key):
        """Test initialization with valid API key."""
        auth = APIKeyAuth(mock_api_key)
        assert auth._api_key == mock_api_key

    def test_init_with_whitespace_key(self):
        """Test initialization trims whitespace from API key."""
        auth = APIKeyAuth("  test-key  ")
        assert auth._api_key == "test-key"

    def test_init_with_empty_key_raises_error(self):
        """Test that empty API key raises ValueError."""
        with pytest.raises(ValueError, match="API key cannot be empty"):
            APIKeyAuth("")

    def test_init_with_whitespace_only_key_raises_error(self):
        """Test that whitespace-only API key raises ValueError."""
        with pytest.raises(ValueError, match="API key cannot be empty"):
            APIKeyAuth("   ")

    def test_init_with_none_raises_error(self):
        """Test that None API key raises ValueError."""
        with pytest.raises(ValueError, match="API key cannot be empty"):
            APIKeyAuth(None)

    def test_get_headers_returns_bearer_token(self, api_key_auth, mock_api_key):
        """Test that get_headers returns proper Authorization header."""
        headers = api_key_auth.get_headers()
        
        expected_headers = {
            "Authorization": f"Bearer {mock_api_key}",
            "Content-Type": "application/json"
        }
        assert headers == expected_headers

    def test_is_valid_returns_true_for_valid_key(self, api_key_auth):
        """Test that is_valid returns True for valid key."""
        assert api_key_auth.is_valid() is True

    def test_is_valid_returns_false_for_empty_key(self):
        """Test that is_valid handles edge cases."""
        # This tests the edge case where _api_key somehow becomes empty
        auth = APIKeyAuth("test")
        auth._api_key = ""
        assert auth.is_valid() is False

        auth._api_key = None
        assert auth.is_valid() is False

    def test_refresh_is_noop(self, api_key_auth):
        """Test that refresh does nothing (API keys don't refresh)."""
        original_key = api_key_auth._api_key
        api_key_auth.refresh()
        assert api_key_auth._api_key == original_key

    def test_api_key_property_masks_key(self):
        """Test that api_key property masks the key for security."""
        # Test short key (<=8 chars)
        auth = APIKeyAuth("short")
        assert auth.api_key == "*****"

        # Test medium key (<=8 chars)
        auth = APIKeyAuth("medium12")
        assert auth.api_key == "********"

        # Test long key (>8 chars) - shows first 4 and last 4
        auth = APIKeyAuth("this-is-a-very-long-api-key-for-testing")
        expected = "this" + "*" * (len("this-is-a-very-long-api-key-for-testing") - 8) + "ting"
        assert auth.api_key == expected

    def test_repr_shows_masked_key(self, mock_api_key):
        """Test that __repr__ shows masked API key."""
        auth = APIKeyAuth(mock_api_key)
        repr_str = repr(auth)
        
        assert "APIKeyAuth" in repr_str
        assert mock_api_key not in repr_str  # Real key should not appear
        assert auth.api_key in repr_str  # Masked key should appear

    def test_validate_credentials_succeeds_for_valid_key(self, api_key_auth):
        """Test that validate_credentials succeeds for valid key."""
        # Should not raise any exception
        api_key_auth.validate_credentials()
        assert api_key_auth.is_valid() is True

    def test_different_key_lengths_mask_correctly(self):
        """Test that different key lengths are masked correctly."""
        test_cases = [
            ("a", "*"),
            ("ab", "**"),
            ("abc", "***"),
            ("abcd", "****"),
            ("abcdefgh", "********"),
            ("abcdefghi", "abcd*fghi"),  # 9 chars: first 4 + 1 star + last 4
            ("abcdefghij", "abcd**ghij"),  # 10 chars: first 4 + 2 stars + last 4
            ("very-long-api-key-here", "very**************here"),  # 22 chars: first 4 + 14 stars + last 4
        ]
        
        for key, expected_mask in test_cases:
            auth = APIKeyAuth(key)
            actual = auth.api_key
            assert actual == expected_mask, f"Failed for key '{key}': expected '{expected_mask}', got '{actual}'"