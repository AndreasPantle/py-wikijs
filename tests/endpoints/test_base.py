"""Tests for base endpoint class."""

from unittest.mock import Mock

import pytest

from wikijs.client import WikiJSClient
from wikijs.endpoints.base import BaseEndpoint


class TestBaseEndpoint:
    """Test suite for BaseEndpoint."""

    @pytest.fixture
    def mock_client(self):
        """Create a mock WikiJS client."""
        client = Mock(spec=WikiJSClient)
        return client

    @pytest.fixture
    def base_endpoint(self, mock_client):
        """Create a BaseEndpoint instance with mock client."""
        return BaseEndpoint(mock_client)

    def test_init(self, mock_client):
        """Test BaseEndpoint initialization."""
        endpoint = BaseEndpoint(mock_client)
        assert endpoint._client is mock_client

    def test_request(self, base_endpoint, mock_client):
        """Test _request method delegates to client."""
        # Setup mock response
        mock_response = {"data": "test"}
        mock_client._request.return_value = mock_response

        # Call _request
        result = base_endpoint._request(
            "GET",
            "/test",
            params={"param": "value"},
            json_data={"data": "test"},
            extra_param="extra",
        )

        # Verify delegation to client
        mock_client._request.assert_called_once_with(
            method="GET",
            endpoint="/test",
            params={"param": "value"},
            json_data={"data": "test"},
            extra_param="extra",
        )

        # Verify response
        assert result == mock_response

    def test_get(self, base_endpoint, mock_client):
        """Test _get method."""
        mock_response = {"data": "test"}
        mock_client._request.return_value = mock_response

        result = base_endpoint._get("/test", params={"param": "value"})

        mock_client._request.assert_called_once_with(
            method="GET",
            endpoint="/test",
            params={"param": "value"},
            json_data=None,
        )
        assert result == mock_response

    def test_post(self, base_endpoint, mock_client):
        """Test _post method."""
        mock_response = {"data": "test"}
        mock_client._request.return_value = mock_response

        result = base_endpoint._post(
            "/test", json_data={"data": "test"}, params={"param": "value"}
        )

        mock_client._request.assert_called_once_with(
            method="POST",
            endpoint="/test",
            params={"param": "value"},
            json_data={"data": "test"},
        )
        assert result == mock_response

    def test_put(self, base_endpoint, mock_client):
        """Test _put method."""
        mock_response = {"data": "test"}
        mock_client._request.return_value = mock_response

        result = base_endpoint._put(
            "/test", json_data={"data": "test"}, params={"param": "value"}
        )

        mock_client._request.assert_called_once_with(
            method="PUT",
            endpoint="/test",
            params={"param": "value"},
            json_data={"data": "test"},
        )
        assert result == mock_response

    def test_delete(self, base_endpoint, mock_client):
        """Test _delete method."""
        mock_response = {"data": "test"}
        mock_client._request.return_value = mock_response

        result = base_endpoint._delete("/test", params={"param": "value"})

        mock_client._request.assert_called_once_with(
            method="DELETE",
            endpoint="/test",
            params={"param": "value"},
            json_data=None,
        )
        assert result == mock_response

    def test_build_endpoint_single_part(self, base_endpoint):
        """Test _build_endpoint with single part."""
        result = base_endpoint._build_endpoint("test")
        assert result == "/test"

    def test_build_endpoint_multiple_parts(self, base_endpoint):
        """Test _build_endpoint with multiple parts."""
        result = base_endpoint._build_endpoint("api", "v1", "pages")
        assert result == "/api/v1/pages"

    def test_build_endpoint_with_slashes(self, base_endpoint):
        """Test _build_endpoint handles leading/trailing slashes."""
        result = base_endpoint._build_endpoint("/api/", "/v1/", "/pages/")
        assert result == "/api/v1/pages"

    def test_build_endpoint_empty_parts(self, base_endpoint):
        """Test _build_endpoint filters out empty parts."""
        result = base_endpoint._build_endpoint("api", "", "pages", None)
        assert result == "/api/pages"

    def test_build_endpoint_numeric_parts(self, base_endpoint):
        """Test _build_endpoint handles numeric parts."""
        result = base_endpoint._build_endpoint("pages", 123, "edit")
        assert result == "/pages/123/edit"
