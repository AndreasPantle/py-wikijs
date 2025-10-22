"""Assets endpoint for Wiki.js API."""

import os
from typing import BinaryIO, Dict, List, Optional, Union

from ..exceptions import APIError, ValidationError
from ..models import Asset, AssetFolder, AssetMove, AssetRename, FolderCreate
from .base import BaseEndpoint


class AssetsEndpoint(BaseEndpoint):
    """Endpoint for managing Wiki.js assets.

    Provides methods to:
    - List assets
    - Get asset details
    - Upload files
    - Download files
    - Rename assets
    - Move assets between folders
    - Delete assets
    - Manage folders
    """

    def list(
        self, folder_id: Optional[int] = None, kind: Optional[str] = None
    ) -> List[Asset]:
        """List all assets, optionally filtered by folder or kind.

        Args:
            folder_id: Filter by folder ID (None for all folders)
            kind: Filter by asset kind (image, binary, etc.)

        Returns:
            List of Asset objects

        Raises:
            ValidationError: If parameters are invalid
            APIError: If the API request fails

        Example:
            >>> assets = client.assets.list()
            >>> images = client.assets.list(kind="image")
            >>> folder_assets = client.assets.list(folder_id=1)
        """
        # Validate folder_id
        if folder_id is not None and folder_id < 0:
            raise ValidationError("folder_id must be non-negative")

        query = """
        query ($folderId: Int, $kind: AssetKind) {
            assets {
                list(folderId: $folderId, kind: $kind) {
                    id
                    filename
                    ext
                    kind
                    mime
                    fileSize
                    folderId
                    folder {
                        id
                        slug
                        name
                    }
                    authorId
                    authorName
                    createdAt
                    updatedAt
                }
            }
        }
        """

        variables = {}
        if folder_id is not None:
            variables["folderId"] = folder_id
        if kind is not None:
            variables["kind"] = kind.upper()

        response = self._post(
            "/graphql", json_data={"query": query, "variables": variables}
        )

        # Check for GraphQL errors
        if "errors" in response:
            raise APIError(f"GraphQL errors: {response['errors']}")

        # Extract and normalize assets
        assets_data = response.get("data", {}).get("assets", {}).get("list", [])
        return [Asset(**self._normalize_asset_data(a)) for a in assets_data]

    def get(self, asset_id: int) -> Asset:
        """Get a specific asset by ID.

        Args:
            asset_id: The asset ID

        Returns:
            Asset object

        Raises:
            ValidationError: If asset_id is invalid
            APIError: If the asset is not found or API request fails

        Example:
            >>> asset = client.assets.get(123)
            >>> print(f"{asset.filename}: {asset.size_mb:.2f} MB")
        """
        # Validate asset_id
        if not isinstance(asset_id, int) or asset_id <= 0:
            raise ValidationError("asset_id must be a positive integer")

        query = """
        query ($id: Int!) {
            assets {
                single(id: $id) {
                    id
                    filename
                    ext
                    kind
                    mime
                    fileSize
                    folderId
                    folder {
                        id
                        slug
                        name
                    }
                    authorId
                    authorName
                    createdAt
                    updatedAt
                }
            }
        }
        """

        response = self._post(
            "/graphql", json_data={"query": query, "variables": {"id": asset_id}}
        )

        # Check for GraphQL errors
        if "errors" in response:
            raise APIError(f"GraphQL errors: {response['errors']}")

        # Extract asset data
        asset_data = response.get("data", {}).get("assets", {}).get("single")

        if not asset_data:
            raise APIError(f"Asset with ID {asset_id} not found")

        return Asset(**self._normalize_asset_data(asset_data))

    def upload(
        self,
        file_path: str,
        folder_id: int = 0,
        filename: Optional[str] = None,
    ) -> Asset:
        """Upload a file as an asset.

        Args:
            file_path: Path to local file to upload
            folder_id: Target folder ID (default: 0 for root)
            filename: Optional custom filename (uses original if not provided)

        Returns:
            Created Asset object

        Raises:
            ValidationError: If file_path is invalid
            APIError: If the upload fails
            FileNotFoundError: If file doesn't exist

        Example:
            >>> asset = client.assets.upload("/path/to/image.png", folder_id=1)
            >>> print(f"Uploaded: {asset.filename}")
        """
        # Validate file path
        if not file_path or not file_path.strip():
            raise ValidationError("file_path cannot be empty")

        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        if not os.path.isfile(file_path):
            raise ValidationError(f"Path is not a file: {file_path}")

        # Validate folder_id
        if folder_id < 0:
            raise ValidationError("folder_id must be non-negative")

        # Get filename
        if filename is None:
            filename = os.path.basename(file_path)

        # For now, use GraphQL mutation
        # Note: Wiki.js may require multipart form upload which would need special handling
        mutation = """
        mutation ($folderId: Int!, $file: Upload!) {
            assets {
                createFile(folderId: $folderId, file: $file) {
                    responseResult {
                        succeeded
                        errorCode
                        slug
                        message
                    }
                    asset {
                        id
                        filename
                        ext
                        kind
                        mime
                        fileSize
                        folderId
                        authorId
                        authorName
                        createdAt
                        updatedAt
                    }
                }
            }
        }
        """

        # Note: Actual file upload would require multipart/form-data
        # This is a simplified version
        raise NotImplementedError(
            "File upload requires multipart form support. "
            "Use the Wiki.js web interface or REST API directly for file uploads."
        )

    def download(self, asset_id: int, output_path: str) -> bool:
        """Download an asset to a local file.

        Args:
            asset_id: The asset ID
            output_path: Local path to save the file

        Returns:
            True if download successful

        Raises:
            ValidationError: If parameters are invalid
            APIError: If the download fails

        Example:
            >>> client.assets.download(123, "/path/to/save/file.png")
        """
        # Validate asset_id
        if not isinstance(asset_id, int) or asset_id <= 0:
            raise ValidationError("asset_id must be a positive integer")

        if not output_path or not output_path.strip():
            raise ValidationError("output_path cannot be empty")

        # Note: Downloading requires REST API endpoint, not GraphQL
        raise NotImplementedError(
            "File download requires REST API support. "
            "Use the Wiki.js REST API directly: GET /a/{assetId}"
        )

    def rename(self, asset_id: int, new_filename: str) -> Asset:
        """Rename an asset.

        Args:
            asset_id: The asset ID
            new_filename: New filename

        Returns:
            Updated Asset object

        Raises:
            ValidationError: If parameters are invalid
            APIError: If the rename fails

        Example:
            >>> asset = client.assets.rename(123, "new-name.png")
        """
        # Validate
        if not isinstance(asset_id, int) or asset_id <= 0:
            raise ValidationError("asset_id must be a positive integer")

        if not new_filename or not new_filename.strip():
            raise ValidationError("new_filename cannot be empty")

        mutation = """
        mutation ($id: Int!, $filename: String!) {
            assets {
                renameAsset(id: $id, filename: $filename) {
                    responseResult {
                        succeeded
                        errorCode
                        slug
                        message
                    }
                    asset {
                        id
                        filename
                        ext
                        kind
                        mime
                        fileSize
                        folderId
                        authorId
                        authorName
                        createdAt
                        updatedAt
                    }
                }
            }
        }
        """

        response = self._post(
            "/graphql",
            json_data={
                "query": mutation,
                "variables": {"id": asset_id, "filename": new_filename.strip()},
            },
        )

        # Check for GraphQL errors
        if "errors" in response:
            raise APIError(f"GraphQL errors: {response['errors']}")

        # Check response result
        result = response.get("data", {}).get("assets", {}).get("renameAsset", {})
        response_result = result.get("responseResult", {})

        if not response_result.get("succeeded"):
            error_msg = response_result.get("message", "Unknown error")
            raise APIError(f"Failed to rename asset: {error_msg}")

        # Extract and return updated asset
        asset_data = result.get("asset")
        if not asset_data:
            raise APIError("Asset renamed but no data returned")

        return Asset(**self._normalize_asset_data(asset_data))

    def move(self, asset_id: int, folder_id: int) -> Asset:
        """Move an asset to a different folder.

        Args:
            asset_id: The asset ID
            folder_id: Target folder ID

        Returns:
            Updated Asset object

        Raises:
            ValidationError: If parameters are invalid
            APIError: If the move fails

        Example:
            >>> asset = client.assets.move(123, folder_id=2)
        """
        # Validate
        if not isinstance(asset_id, int) or asset_id <= 0:
            raise ValidationError("asset_id must be a positive integer")

        if not isinstance(folder_id, int) or folder_id < 0:
            raise ValidationError("folder_id must be non-negative")

        mutation = """
        mutation ($id: Int!, $folderId: Int!) {
            assets {
                moveAsset(id: $id, folderId: $folderId) {
                    responseResult {
                        succeeded
                        errorCode
                        slug
                        message
                    }
                    asset {
                        id
                        filename
                        ext
                        kind
                        mime
                        fileSize
                        folderId
                        folder {
                            id
                            slug
                            name
                        }
                        authorId
                        authorName
                        createdAt
                        updatedAt
                    }
                }
            }
        }
        """

        response = self._post(
            "/graphql",
            json_data={
                "query": mutation,
                "variables": {"id": asset_id, "folderId": folder_id},
            },
        )

        # Check for GraphQL errors
        if "errors" in response:
            raise APIError(f"GraphQL errors: {response['errors']}")

        # Check response result
        result = response.get("data", {}).get("assets", {}).get("moveAsset", {})
        response_result = result.get("responseResult", {})

        if not response_result.get("succeeded"):
            error_msg = response_result.get("message", "Unknown error")
            raise APIError(f"Failed to move asset: {error_msg}")

        # Extract and return updated asset
        asset_data = result.get("asset")
        if not asset_data:
            raise APIError("Asset moved but no data returned")

        return Asset(**self._normalize_asset_data(asset_data))

    def delete(self, asset_id: int) -> bool:
        """Delete an asset.

        Args:
            asset_id: The asset ID

        Returns:
            True if deletion was successful

        Raises:
            ValidationError: If asset_id is invalid
            APIError: If the deletion fails

        Example:
            >>> success = client.assets.delete(123)
        """
        # Validate asset_id
        if not isinstance(asset_id, int) or asset_id <= 0:
            raise ValidationError("asset_id must be a positive integer")

        mutation = """
        mutation ($id: Int!) {
            assets {
                deleteAsset(id: $id) {
                    responseResult {
                        succeeded
                        errorCode
                        slug
                        message
                    }
                }
            }
        }
        """

        response = self._post(
            "/graphql", json_data={"query": mutation, "variables": {"id": asset_id}}
        )

        # Check for GraphQL errors
        if "errors" in response:
            raise APIError(f"GraphQL errors: {response['errors']}")

        # Check response result
        result = response.get("data", {}).get("assets", {}).get("deleteAsset", {})
        response_result = result.get("responseResult", {})

        if not response_result.get("succeeded"):
            error_msg = response_result.get("message", "Unknown error")
            raise APIError(f"Failed to delete asset: {error_msg}")

        return True

    def list_folders(self) -> List[AssetFolder]:
        """List all asset folders.

        Returns:
            List of AssetFolder objects

        Raises:
            APIError: If the API request fails

        Example:
            >>> folders = client.assets.list_folders()
            >>> for folder in folders:
            ...     print(f"{folder.name}: {folder.slug}")
        """
        query = """
        query {
            assets {
                folders {
                    id
                    slug
                    name
                }
            }
        }
        """

        response = self._post("/graphql", json_data={"query": query})

        # Check for GraphQL errors
        if "errors" in response:
            raise APIError(f"GraphQL errors: {response['errors']}")

        # Extract folders
        folders_data = response.get("data", {}).get("assets", {}).get("folders", [])
        return [AssetFolder(**folder) for folder in folders_data]

    def create_folder(self, slug: str, name: Optional[str] = None) -> AssetFolder:
        """Create a new asset folder.

        Args:
            slug: Folder slug/path
            name: Optional folder name

        Returns:
            Created AssetFolder object

        Raises:
            ValidationError: If slug is invalid
            APIError: If folder creation fails

        Example:
            >>> folder = client.assets.create_folder("documents", "Documents")
        """
        # Validate
        if not slug or not slug.strip():
            raise ValidationError("slug cannot be empty")

        # Clean slug
        slug = slug.strip().strip("/")
        if not slug:
            raise ValidationError("slug cannot be just slashes")

        mutation = """
        mutation ($slug: String!, $name: String) {
            assets {
                createFolder(slug: $slug, name: $name) {
                    responseResult {
                        succeeded
                        errorCode
                        slug
                        message
                    }
                    folder {
                        id
                        slug
                        name
                    }
                }
            }
        }
        """

        variables = {"slug": slug}
        if name:
            variables["name"] = name

        response = self._post(
            "/graphql", json_data={"query": mutation, "variables": variables}
        )

        # Check for GraphQL errors
        if "errors" in response:
            raise APIError(f"GraphQL errors: {response['errors']}")

        # Check response result
        result = response.get("data", {}).get("assets", {}).get("createFolder", {})
        response_result = result.get("responseResult", {})

        if not response_result.get("succeeded"):
            error_msg = response_result.get("message", "Unknown error")
            raise APIError(f"Failed to create folder: {error_msg}")

        # Extract and return folder
        folder_data = result.get("folder")
        if not folder_data:
            raise APIError("Folder created but no data returned")

        return AssetFolder(**folder_data)

    def delete_folder(self, folder_id: int) -> bool:
        """Delete an asset folder.

        Args:
            folder_id: The folder ID

        Returns:
            True if deletion was successful

        Raises:
            ValidationError: If folder_id is invalid
            APIError: If the deletion fails

        Example:
            >>> success = client.assets.delete_folder(5)
        """
        # Validate folder_id
        if not isinstance(folder_id, int) or folder_id <= 0:
            raise ValidationError("folder_id must be a positive integer")

        mutation = """
        mutation ($id: Int!) {
            assets {
                deleteFolder(id: $id) {
                    responseResult {
                        succeeded
                        errorCode
                        slug
                        message
                    }
                }
            }
        }
        """

        response = self._post(
            "/graphql", json_data={"query": mutation, "variables": {"id": folder_id}}
        )

        # Check for GraphQL errors
        if "errors" in response:
            raise APIError(f"GraphQL errors: {response['errors']}")

        # Check response result
        result = response.get("data", {}).get("assets", {}).get("deleteFolder", {})
        response_result = result.get("responseResult", {})

        if not response_result.get("succeeded"):
            error_msg = response_result.get("message", "Unknown error")
            raise APIError(f"Failed to delete folder: {error_msg}")

        return True

    def _normalize_asset_data(self, data: Dict) -> Dict:
        """Normalize asset data from API response to Python naming convention.

        Args:
            data: Raw asset data from API

        Returns:
            Normalized asset data with snake_case field names
        """
        normalized = {
            "id": data.get("id"),
            "filename": data.get("filename"),
            "ext": data.get("ext"),
            "kind": data.get("kind"),
            "mime": data.get("mime"),
            "file_size": data.get("fileSize"),
            "folder_id": data.get("folderId"),
            "folder": data.get("folder"),
            "author_id": data.get("authorId"),
            "author_name": data.get("authorName"),
            "created_at": data.get("createdAt"),
            "updated_at": data.get("updatedAt"),
        }

        return normalized
