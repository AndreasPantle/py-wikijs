"""Tests for Assets endpoint."""

from unittest.mock import Mock

import pytest

from wikijs.endpoints import AssetsEndpoint
from wikijs.exceptions import APIError, ValidationError
from wikijs.models import Asset, AssetFolder


class TestAssetsEndpoint:
    """Test AssetsEndpoint class."""

    @pytest.fixture
    def client(self):
        """Create mock client."""
        mock_client = Mock()
        mock_client.base_url = "https://wiki.example.com"
        return mock_client

    @pytest.fixture
    def endpoint(self, client):
        """Create AssetsEndpoint instance."""
        return AssetsEndpoint(client)

    def test_list_assets(self, endpoint):
        """Test listing assets."""
        mock_response = {
            "data": {
                "assets": {
                    "list": [
                        {
                            "id": 1,
                            "filename": "test.png",
                            "ext": "png",
                            "kind": "image",
                            "mime": "image/png",
                            "fileSize": 1024,
                            "folderId": 0,
                            "folder": None,
                            "authorId": 1,
                            "authorName": "Admin",
                            "createdAt": "2024-01-01T00:00:00Z",
                            "updatedAt": "2024-01-01T00:00:00Z",
                        }
                    ]
                }
            }
        }
        endpoint._post = Mock(return_value=mock_response)

        assets = endpoint.list()

        assert len(assets) == 1
        assert isinstance(assets[0], Asset)
        assert assets[0].filename == "test.png"

    def test_get_asset(self, endpoint):
        """Test getting an asset."""
        mock_response = {
            "data": {
                "assets": {
                    "single": {
                        "id": 1,
                        "filename": "test.png",
                        "ext": "png",
                        "kind": "image",
                        "mime": "image/png",
                        "fileSize": 1024,
                        "folderId": 0,
                        "folder": None,
                        "authorId": 1,
                        "authorName": "Admin",
                        "createdAt": "2024-01-01T00:00:00Z",
                        "updatedAt": "2024-01-01T00:00:00Z",
                    }
                }
            }
        }
        endpoint._post = Mock(return_value=mock_response)

        asset = endpoint.get(1)

        assert isinstance(asset, Asset)
        assert asset.id == 1

    def test_rename_asset(self, endpoint):
        """Test renaming an asset."""
        mock_response = {
            "data": {
                "assets": {
                    "renameAsset": {
                        "responseResult": {"succeeded": True},
                        "asset": {
                            "id": 1,
                            "filename": "newname.png",
                            "ext": "png",
                            "kind": "image",
                            "mime": "image/png",
                            "fileSize": 1024,
                            "folderId": 0,
                            "authorId": 1,
                            "authorName": "Admin",
                            "createdAt": "2024-01-01T00:00:00Z",
                            "updatedAt": "2024-01-01T00:00:00Z",
                        },
                    }
                }
            }
        }
        endpoint._post = Mock(return_value=mock_response)

        asset = endpoint.rename(1, "newname.png")

        assert asset.filename == "newname.png"

    def test_delete_asset(self, endpoint):
        """Test deleting an asset."""
        mock_response = {
            "data": {
                "assets": {
                    "deleteAsset": {
                        "responseResult": {"succeeded": True}
                    }
                }
            }
        }
        endpoint._post = Mock(return_value=mock_response)

        result = endpoint.delete(1)

        assert result is True

    def test_list_folders(self, endpoint):
        """Test listing folders."""
        mock_response = {
            "data": {
                "assets": {
                    "folders": [
                        {"id": 1, "slug": "documents", "name": "Documents"}
                    ]
                }
            }
        }
        endpoint._post = Mock(return_value=mock_response)

        folders = endpoint.list_folders()

        assert len(folders) == 1
        assert isinstance(folders[0], AssetFolder)
        assert folders[0].slug == "documents"

    def test_validation_errors(self, endpoint):
        """Test validation errors."""
        with pytest.raises(ValidationError):
            endpoint.get(0)

        with pytest.raises(ValidationError):
            endpoint.delete(-1)

        with pytest.raises(ValidationError):
            endpoint.rename(1, "")
