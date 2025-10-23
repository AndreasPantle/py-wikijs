"""Async assets endpoint for Wiki.js API."""

import os
from typing import Dict, List, Optional

from ...exceptions import APIError, ValidationError
from ...models import Asset, AssetFolder
from .base import AsyncBaseEndpoint


class AsyncAssetsEndpoint(AsyncBaseEndpoint):
    """Async endpoint for managing Wiki.js assets."""

    async def list(
        self, folder_id: Optional[int] = None, kind: Optional[str] = None
    ) -> List[Asset]:
        """List all assets asynchronously."""
        if folder_id is not None and folder_id < 0:
            raise ValidationError("folder_id must be non-negative")

        query = """
        query ($folderId: Int, $kind: AssetKind) {
            assets {
                list(folderId: $folderId, kind: $kind) {
                    id filename ext kind mime fileSize folderId
                    folder { id slug name }
                    authorId authorName createdAt updatedAt
                }
            }
        }
        """

        variables = {}
        if folder_id is not None:
            variables["folderId"] = folder_id
        if kind is not None:
            variables["kind"] = kind.upper()

        response = await self._post(
            "/graphql", json_data={"query": query, "variables": variables}
        )

        if "errors" in response:
            raise APIError(f"GraphQL errors: {response['errors']}")

        assets_data = response.get("data", {}).get("assets", {}).get("list", [])
        return [Asset(**self._normalize_asset_data(a)) for a in assets_data]

    async def get(self, asset_id: int) -> Asset:
        """Get a specific asset by ID asynchronously."""
        if not isinstance(asset_id, int) or asset_id <= 0:
            raise ValidationError("asset_id must be a positive integer")

        query = """
        query ($id: Int!) {
            assets {
                single(id: $id) {
                    id filename ext kind mime fileSize folderId
                    folder { id slug name }
                    authorId authorName createdAt updatedAt
                }
            }
        }
        """

        response = await self._post(
            "/graphql", json_data={"query": query, "variables": {"id": asset_id}}
        )

        if "errors" in response:
            raise APIError(f"GraphQL errors: {response['errors']}")

        asset_data = response.get("data", {}).get("assets", {}).get("single")

        if not asset_data:
            raise APIError(f"Asset with ID {asset_id} not found")

        return Asset(**self._normalize_asset_data(asset_data))

    async def rename(self, asset_id: int, new_filename: str) -> Asset:
        """Rename an asset asynchronously."""
        if not isinstance(asset_id, int) or asset_id <= 0:
            raise ValidationError("asset_id must be a positive integer")

        if not new_filename or not new_filename.strip():
            raise ValidationError("new_filename cannot be empty")

        mutation = """
        mutation ($id: Int!, $filename: String!) {
            assets {
                renameAsset(id: $id, filename: $filename) {
                    responseResult { succeeded errorCode slug message }
                    asset {
                        id filename ext kind mime fileSize folderId
                        authorId authorName createdAt updatedAt
                    }
                }
            }
        }
        """

        response = await self._post(
            "/graphql",
            json_data={
                "query": mutation,
                "variables": {"id": asset_id, "filename": new_filename.strip()},
            },
        )

        if "errors" in response:
            raise APIError(f"GraphQL errors: {response['errors']}")

        result = response.get("data", {}).get("assets", {}).get("renameAsset", {})
        response_result = result.get("responseResult", {})

        if not response_result.get("succeeded"):
            error_msg = response_result.get("message", "Unknown error")
            raise APIError(f"Failed to rename asset: {error_msg}")

        asset_data = result.get("asset")
        if not asset_data:
            raise APIError("Asset renamed but no data returned")

        return Asset(**self._normalize_asset_data(asset_data))

    async def move(self, asset_id: int, folder_id: int) -> Asset:
        """Move an asset to a different folder asynchronously."""
        if not isinstance(asset_id, int) or asset_id <= 0:
            raise ValidationError("asset_id must be a positive integer")

        if not isinstance(folder_id, int) or folder_id < 0:
            raise ValidationError("folder_id must be non-negative")

        mutation = """
        mutation ($id: Int!, $folderId: Int!) {
            assets {
                moveAsset(id: $id, folderId: $folderId) {
                    responseResult { succeeded errorCode slug message }
                    asset {
                        id filename ext kind mime fileSize folderId
                        folder { id slug name }
                        authorId authorName createdAt updatedAt
                    }
                }
            }
        }
        """

        response = await self._post(
            "/graphql",
            json_data={
                "query": mutation,
                "variables": {"id": asset_id, "folderId": folder_id},
            },
        )

        if "errors" in response:
            raise APIError(f"GraphQL errors: {response['errors']}")

        result = response.get("data", {}).get("assets", {}).get("moveAsset", {})
        response_result = result.get("responseResult", {})

        if not response_result.get("succeeded"):
            error_msg = response_result.get("message", "Unknown error")
            raise APIError(f"Failed to move asset: {error_msg}")

        asset_data = result.get("asset")
        if not asset_data:
            raise APIError("Asset moved but no data returned")

        return Asset(**self._normalize_asset_data(asset_data))

    async def delete(self, asset_id: int) -> bool:
        """Delete an asset asynchronously."""
        if not isinstance(asset_id, int) or asset_id <= 0:
            raise ValidationError("asset_id must be a positive integer")

        mutation = """
        mutation ($id: Int!) {
            assets {
                deleteAsset(id: $id) {
                    responseResult { succeeded errorCode slug message }
                }
            }
        }
        """

        response = await self._post(
            "/graphql", json_data={"query": mutation, "variables": {"id": asset_id}}
        )

        if "errors" in response:
            raise APIError(f"GraphQL errors: {response['errors']}")

        result = response.get("data", {}).get("assets", {}).get("deleteAsset", {})
        response_result = result.get("responseResult", {})

        if not response_result.get("succeeded"):
            error_msg = response_result.get("message", "Unknown error")
            raise APIError(f"Failed to delete asset: {error_msg}")

        return True

    async def list_folders(self) -> List[AssetFolder]:
        """List all asset folders asynchronously."""
        query = """
        query {
            assets {
                folders {
                    id slug name
                }
            }
        }
        """

        response = await self._post("/graphql", json_data={"query": query})

        if "errors" in response:
            raise APIError(f"GraphQL errors: {response['errors']}")

        folders_data = response.get("data", {}).get("assets", {}).get("folders", [])
        return [AssetFolder(**folder) for folder in folders_data]

    async def create_folder(self, slug: str, name: Optional[str] = None) -> AssetFolder:
        """Create a new asset folder asynchronously."""
        if not slug or not slug.strip():
            raise ValidationError("slug cannot be empty")

        slug = slug.strip().strip("/")
        if not slug:
            raise ValidationError("slug cannot be just slashes")

        mutation = """
        mutation ($slug: String!, $name: String) {
            assets {
                createFolder(slug: $slug, name: $name) {
                    responseResult { succeeded errorCode slug message }
                    folder { id slug name }
                }
            }
        }
        """

        variables = {"slug": slug}
        if name:
            variables["name"] = name

        response = await self._post(
            "/graphql", json_data={"query": mutation, "variables": variables}
        )

        if "errors" in response:
            raise APIError(f"GraphQL errors: {response['errors']}")

        result = response.get("data", {}).get("assets", {}).get("createFolder", {})
        response_result = result.get("responseResult", {})

        if not response_result.get("succeeded"):
            error_msg = response_result.get("message", "Unknown error")
            raise APIError(f"Failed to create folder: {error_msg}")

        folder_data = result.get("folder")
        if not folder_data:
            raise APIError("Folder created but no data returned")

        return AssetFolder(**folder_data)

    async def delete_folder(self, folder_id: int) -> bool:
        """Delete an asset folder asynchronously."""
        if not isinstance(folder_id, int) or folder_id <= 0:
            raise ValidationError("folder_id must be a positive integer")

        mutation = """
        mutation ($id: Int!) {
            assets {
                deleteFolder(id: $id) {
                    responseResult { succeeded errorCode slug message }
                }
            }
        }
        """

        response = await self._post(
            "/graphql", json_data={"query": mutation, "variables": {"id": folder_id}}
        )

        if "errors" in response:
            raise APIError(f"GraphQL errors: {response['errors']}")

        result = response.get("data", {}).get("assets", {}).get("deleteFolder", {})
        response_result = result.get("responseResult", {})

        if not response_result.get("succeeded"):
            error_msg = response_result.get("message", "Unknown error")
            raise APIError(f"Failed to delete folder: {error_msg}")

        return True

    def _normalize_asset_data(self, data: Dict) -> Dict:
        """Normalize asset data from API response."""
        return {
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

    async def iter_all(
        self,
        batch_size: int = 50,
        folder_id: Optional[int] = None,
        kind: Optional[str] = None,
    ):
        """Iterate over all assets asynchronously with automatic pagination.

        Args:
            batch_size: Batch size for iteration (default: 50)
            folder_id: Filter by folder ID
            kind: Filter by asset kind

        Yields:
            Asset objects one at a time

        Example:
            >>> async for asset in client.assets.iter_all(kind="image"):
            ...     print(f"{asset.filename}: {asset.size_mb:.2f} MB")
        """
        assets = await self.list(folder_id=folder_id, kind=kind)

        # Yield in batches to limit memory usage
        for i in range(0, len(assets), batch_size):
            batch = assets[i : i + batch_size]
            for asset in batch:
                yield asset
