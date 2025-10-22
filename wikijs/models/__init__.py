"""Data models for wikijs-python-sdk."""

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
    "BaseModel",
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
