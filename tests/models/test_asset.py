"""Tests for Asset data models."""

import pytest
from pydantic import ValidationError

from wikijs.models import Asset, AssetFolder, AssetRename, AssetMove, FolderCreate


class TestAsset:
    """Test Asset model."""

    def test_asset_creation_minimal(self):
        """Test creating an asset with minimal fields."""
        asset = Asset(
            id=1,
            filename="test.png",
            ext="png",
            kind="image",
            mime="image/png",
            file_size=1024,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        assert asset.id == 1
        assert asset.filename == "test.png"
        assert asset.file_size == 1024

    def test_asset_size_helpers(self):
        """Test size helper methods."""
        asset = Asset(
            id=1,
            filename="test.png",
            ext="png",
            kind="image",
            mime="image/png",
            file_size=1048576,  # 1 MB
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        assert asset.size_mb == 1.0
        assert asset.size_kb == 1024.0

    def test_asset_filename_validation(self):
        """Test filename validation."""
        with pytest.raises(ValidationError):
            Asset(
                id=1,
                filename="",
                ext="png",
                kind="image",
                mime="image/png",
                file_size=1024,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
            )


class TestAssetRename:
    """Test AssetRename model."""

    def test_asset_rename_valid(self):
        """Test valid asset rename."""
        rename = AssetRename(asset_id=1, new_filename="newname.png")
        assert rename.asset_id == 1
        assert rename.new_filename == "newname.png"

    def test_asset_rename_validation(self):
        """Test validation."""
        with pytest.raises(ValidationError):
            AssetRename(asset_id=0, new_filename="test.png")

        with pytest.raises(ValidationError):
            AssetRename(asset_id=1, new_filename="")


class TestFolderCreate:
    """Test FolderCreate model."""

    def test_folder_create_valid(self):
        """Test valid folder creation."""
        folder = FolderCreate(slug="documents", name="Documents")
        assert folder.slug == "documents"
        assert folder.name == "Documents"

    def test_folder_create_slug_validation(self):
        """Test slug validation."""
        with pytest.raises(ValidationError):
            FolderCreate(slug="")

        with pytest.raises(ValidationError):
            FolderCreate(slug="///")

    def test_folder_create_slug_normalization(self):
        """Test slug normalization."""
        folder = FolderCreate(slug="/documents/", name="Documents")
        assert folder.slug == "documents"
