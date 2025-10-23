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

    # Move operations
    def test_move_asset(self, endpoint):
        """Test moving an asset to a different folder."""
        mock_response = {
            "data": {
                "assets": {
                    "moveAsset": {
                        "responseResult": {"succeeded": True},
                        "asset": {
                            "id": 1,
                            "filename": "test.png",
                            "ext": "png",
                            "kind": "image",
                            "mime": "image/png",
                            "fileSize": 1024,
                            "folderId": 5,
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

        asset = endpoint.move(1, 5)

        assert asset.folder_id == 5

    def test_move_asset_validation_error(self, endpoint):
        """Test move asset with invalid inputs."""
        with pytest.raises(ValidationError):
            endpoint.move(0, 1)  # Invalid asset ID

        with pytest.raises(ValidationError):
            endpoint.move(1, -1)  # Invalid folder ID

    # Folder operations
    def test_create_folder(self, endpoint):
        """Test creating a folder."""
        mock_response = {
            "data": {
                "assets": {
                    "createFolder": {
                        "responseResult": {"succeeded": True},
                        "folder": {"id": 1, "slug": "documents", "name": "Documents"},
                    }
                }
            }
        }
        endpoint._post = Mock(return_value=mock_response)

        folder = endpoint.create_folder("documents", "Documents")

        assert isinstance(folder, AssetFolder)
        assert folder.slug == "documents"
        assert folder.name == "Documents"

    def test_create_folder_minimal(self, endpoint):
        """Test creating a folder with minimal parameters."""
        mock_response = {
            "data": {
                "assets": {
                    "createFolder": {
                        "responseResult": {"succeeded": True},
                        "folder": {"id": 2, "slug": "images", "name": None},
                    }
                }
            }
        }
        endpoint._post = Mock(return_value=mock_response)

        folder = endpoint.create_folder("images")

        assert folder.slug == "images"
        assert folder.name is None

    def test_create_folder_validation_error(self, endpoint):
        """Test create folder with invalid slug."""
        with pytest.raises(ValidationError):
            endpoint.create_folder("")  # Empty slug

        with pytest.raises(ValidationError):
            endpoint.create_folder("///")  # Just slashes

    def test_delete_folder(self, endpoint):
        """Test deleting a folder."""
        mock_response = {
            "data": {
                "assets": {
                    "deleteFolder": {
                        "responseResult": {"succeeded": True}
                    }
                }
            }
        }
        endpoint._post = Mock(return_value=mock_response)

        result = endpoint.delete_folder(1)

        assert result is True

    def test_delete_folder_validation_error(self, endpoint):
        """Test delete folder with invalid ID."""
        with pytest.raises(ValidationError):
            endpoint.delete_folder(0)

        with pytest.raises(ValidationError):
            endpoint.delete_folder(-1)

    # List operations with filters
    def test_list_assets_with_folder_filter(self, endpoint):
        """Test listing assets filtered by folder."""
        mock_response = {
            "data": {
                "assets": {
                    "list": [
                        {
                            "id": 1,
                            "filename": "doc.pdf",
                            "ext": "pdf",
                            "kind": "binary",
                            "mime": "application/pdf",
                            "fileSize": 2048,
                            "folderId": 1,
                            "folder": {"id": 1, "slug": "documents", "name": "Documents"},
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

        assets = endpoint.list(folder_id=1)

        assert len(assets) == 1
        assert assets[0].folder_id == 1

    def test_list_assets_with_kind_filter(self, endpoint):
        """Test listing assets filtered by kind."""
        mock_response = {
            "data": {
                "assets": {
                    "list": [
                        {
                            "id": 1,
                            "filename": "photo.jpg",
                            "ext": "jpg",
                            "kind": "image",
                            "mime": "image/jpeg",
                            "fileSize": 5120,
                            "folderId": 0,
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

        assets = endpoint.list(kind="image")

        assert len(assets) == 1
        assert assets[0].kind == "image"

    def test_list_assets_empty(self, endpoint):
        """Test listing assets when none exist."""
        mock_response = {"data": {"assets": {"list": []}}}
        endpoint._post = Mock(return_value=mock_response)

        assets = endpoint.list()

        assert len(assets) == 0

    # Error handling
    def test_get_asset_not_found(self, endpoint):
        """Test getting non-existent asset."""
        mock_response = {
            "data": {"assets": {"single": None}},
            "errors": [{"message": "Asset not found"}],
        }
        endpoint._post = Mock(return_value=mock_response)

        with pytest.raises(APIError, match="Asset not found"):
            endpoint.get(999)

    def test_delete_asset_failure(self, endpoint):
        """Test delete asset API failure."""
        mock_response = {
            "data": {
                "assets": {
                    "deleteAsset": {
                        "responseResult": {"succeeded": False, "message": "Permission denied"}
                    }
                }
            }
        }
        endpoint._post = Mock(return_value=mock_response)

        with pytest.raises(APIError, match="Permission denied"):
            endpoint.delete(1)

    def test_rename_asset_failure(self, endpoint):
        """Test rename asset API failure."""
        mock_response = {
            "data": {
                "assets": {
                    "renameAsset": {
                        "responseResult": {"succeeded": False, "message": "Name already exists"}
                    }
                }
            }
        }
        endpoint._post = Mock(return_value=mock_response)

        with pytest.raises(APIError, match="Name already exists"):
            endpoint.rename(1, "duplicate.png")

    def test_move_asset_failure(self, endpoint):
        """Test move asset API failure."""
        mock_response = {
            "data": {
                "assets": {
                    "moveAsset": {
                        "responseResult": {"succeeded": False, "message": "Folder not found"}
                    }
                }
            }
        }
        endpoint._post = Mock(return_value=mock_response)

        with pytest.raises(APIError, match="Folder not found"):
            endpoint.move(1, 999)

    def test_create_folder_failure(self, endpoint):
        """Test create folder API failure."""
        mock_response = {
            "data": {
                "assets": {
                    "createFolder": {
                        "responseResult": {"succeeded": False, "message": "Folder already exists"}
                    }
                }
            }
        }
        endpoint._post = Mock(return_value=mock_response)

        with pytest.raises(APIError, match="Folder already exists"):
            endpoint.create_folder("existing")

    def test_delete_folder_failure(self, endpoint):
        """Test delete folder API failure."""
        mock_response = {
            "data": {
                "assets": {
                    "deleteFolder": {
                        "responseResult": {"succeeded": False, "message": "Folder not empty"}
                    }
                }
            }
        }
        endpoint._post = Mock(return_value=mock_response)

        with pytest.raises(APIError, match="Folder not empty"):
            endpoint.delete_folder(1)

    # Pagination
    def test_iter_all_assets(self, endpoint):
        """Test iterating over all assets with pagination."""
        # First page (smaller batch to ensure pagination works)
        mock_response_page1 = {
            "data": {
                "assets": {
                    "list": [
                        {
                            "id": i,
                            "filename": f"file{i}.png",
                            "ext": "png",
                            "kind": "image",
                            "mime": "image/png",
                            "fileSize": 1024,
                            "folderId": 0,
                            "authorId": 1,
                            "authorName": "Admin",
                            "createdAt": "2024-01-01T00:00:00Z",
                            "updatedAt": "2024-01-01T00:00:00Z",
                        }
                        for i in range(1, 6)  # 5 items
                    ]
                }
            }
        }

        # Second page (empty - pagination stops)
        mock_response_page2 = {"data": {"assets": {"list": []}}}

        endpoint._post = Mock(
            side_effect=[mock_response_page1, mock_response_page2]
        )

        all_assets = list(endpoint.iter_all(batch_size=5))

        assert len(all_assets) == 5
        assert all_assets[0].id == 1
        assert all_assets[4].id == 5

    # Normalization edge cases
    def test_normalize_asset_data_minimal(self, endpoint):
        """Test normalizing asset data with minimal fields."""
        data = {
            "id": 1,
            "filename": "test.png",
            "ext": "png",
            "kind": "image",
            "mime": "image/png",
            "fileSize": 1024,
        }

        normalized = endpoint._normalize_asset_data(data)

        assert normalized["id"] == 1
        assert normalized["filename"] == "test.png"
        # Check that snake_case fields are present
        assert "file_size" in normalized
        assert normalized["file_size"] == 1024

    def test_list_folders_empty(self, endpoint):
        """Test listing folders when none exist."""
        mock_response = {"data": {"assets": {"folders": []}}}
        endpoint._post = Mock(return_value=mock_response)

        folders = endpoint.list_folders()

        assert len(folders) == 0
