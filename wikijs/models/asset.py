"""Data models for Wiki.js assets."""

from typing import Optional

from pydantic import Field, field_validator

from .base import BaseModel, TimestampedModel


class AssetFolder(BaseModel):
    """Asset folder model."""

    id: int = Field(..., description="Folder ID")
    slug: str = Field(..., description="Folder slug/path")
    name: Optional[str] = Field(None, description="Folder name")

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class Asset(TimestampedModel):
    """Wiki.js asset model.

    Represents a file asset (image, document, etc.) in Wiki.js.

    Attributes:
        id: Asset ID
        filename: Original filename
        ext: File extension
        kind: Asset kind (image, binary, etc.)
        mime: MIME type
        file_size: File size in bytes
        folder_id: Parent folder ID
        folder: Parent folder information
        author_id: ID of user who uploaded
        author_name: Name of user who uploaded
        created_at: Upload timestamp
        updated_at: Last update timestamp
    """

    id: int = Field(..., description="Asset ID")
    filename: str = Field(..., min_length=1, description="Original filename")
    ext: str = Field(..., description="File extension")
    kind: str = Field(..., description="Asset kind (image, binary, etc.)")
    mime: str = Field(..., description="MIME type")
    file_size: int = Field(
        ..., alias="fileSize", ge=0, description="File size in bytes"
    )
    folder_id: Optional[int] = Field(
        None, alias="folderId", description="Parent folder ID"
    )
    folder: Optional[AssetFolder] = Field(None, description="Parent folder")
    author_id: Optional[int] = Field(None, alias="authorId", description="Author ID")
    author_name: Optional[str] = Field(
        None, alias="authorName", description="Author name"
    )

    @field_validator("filename")
    @classmethod
    def validate_filename(cls, v: str) -> str:
        """Validate filename."""
        if not v or not v.strip():
            raise ValueError("Filename cannot be empty")
        return v.strip()

    @property
    def size_mb(self) -> float:
        """Get file size in megabytes."""
        return self.file_size / (1024 * 1024)

    @property
    def size_kb(self) -> float:
        """Get file size in kilobytes."""
        return self.file_size / 1024

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class AssetUpload(BaseModel):
    """Model for uploading a new asset.

    Attributes:
        file_path: Local path to file to upload
        folder_id: Target folder ID (default: 0 for root)
        filename: Optional custom filename (uses file_path name if not provided)
    """

    file_path: str = Field(..., alias="filePath", description="Local file path")
    folder_id: int = Field(default=0, alias="folderId", description="Target folder ID")
    filename: Optional[str] = Field(None, description="Custom filename")

    @field_validator("file_path")
    @classmethod
    def validate_file_path(cls, v: str) -> str:
        """Validate file path."""
        if not v or not v.strip():
            raise ValueError("File path cannot be empty")
        return v.strip()

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class AssetRename(BaseModel):
    """Model for renaming an asset.

    Attributes:
        asset_id: Asset ID to rename
        new_filename: New filename
    """

    asset_id: int = Field(..., alias="assetId", description="Asset ID")
    new_filename: str = Field(
        ..., alias="newFilename", min_length=1, description="New filename"
    )

    @field_validator("asset_id")
    @classmethod
    def validate_asset_id(cls, v: int) -> int:
        """Validate asset ID."""
        if v <= 0:
            raise ValueError("Asset ID must be positive")
        return v

    @field_validator("new_filename")
    @classmethod
    def validate_filename(cls, v: str) -> str:
        """Validate filename."""
        if not v or not v.strip():
            raise ValueError("Filename cannot be empty")
        return v.strip()

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class AssetMove(BaseModel):
    """Model for moving an asset to a different folder.

    Attributes:
        asset_id: Asset ID to move
        folder_id: Target folder ID
    """

    asset_id: int = Field(..., alias="assetId", description="Asset ID")
    folder_id: int = Field(..., alias="folderId", description="Target folder ID")

    @field_validator("asset_id")
    @classmethod
    def validate_asset_id(cls, v: int) -> int:
        """Validate asset ID."""
        if v <= 0:
            raise ValueError("Asset ID must be positive")
        return v

    @field_validator("folder_id")
    @classmethod
    def validate_folder_id(cls, v: int) -> int:
        """Validate folder ID."""
        if v < 0:
            raise ValueError("Folder ID must be non-negative")
        return v

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class FolderCreate(BaseModel):
    """Model for creating a new folder.

    Attributes:
        slug: Folder slug/path
        name: Optional folder name
    """

    slug: str = Field(..., min_length=1, description="Folder slug/path")
    name: Optional[str] = Field(None, description="Folder name")

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        """Validate slug."""
        if not v or not v.strip():
            raise ValueError("Slug cannot be empty")
        # Remove leading/trailing slashes
        v = v.strip().strip("/")
        if not v:
            raise ValueError("Slug cannot be just slashes")
        return v

    class Config:
        """Pydantic configuration."""

        populate_by_name = True
