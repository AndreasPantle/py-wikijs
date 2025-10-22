"""Data models for wikijs-python-sdk."""

from .asset import (
    Asset,
    AssetFolder,
    AssetMove,
    AssetRename,
    AssetUpload,
    FolderCreate,
)
from .base import BaseModel
from .group import (
    Group,
    GroupAssignUser,
    GroupCreate,
    GroupPageRule,
    GroupPermission,
    GroupUnassignUser,
    GroupUpdate,
    GroupUser,
)
from .page import Page, PageCreate, PageUpdate
from .user import User, UserCreate, UserGroup, UserUpdate

__all__ = [
    "Asset",
    "AssetFolder",
    "AssetMove",
    "AssetRename",
    "AssetUpload",
    "BaseModel",
    "FolderCreate",
    "Group",
    "GroupAssignUser",
    "GroupCreate",
    "GroupPageRule",
    "GroupPermission",
    "GroupUnassignUser",
    "GroupUpdate",
    "GroupUser",
    "Page",
    "PageCreate",
    "PageUpdate",
    "User",
    "UserCreate",
    "UserUpdate",
    "UserGroup",
]
