"""API endpoints module for wikijs-python-sdk.

This module contains endpoint handlers for different
Wiki.js API endpoints.

Implemented:
- Pages API (CRUD operations) ✅
- Users API (user management) ✅
- Groups API (group management) ✅
- Assets API (file/asset management) ✅

Future implementations:
- System API (system information)
"""

from .assets import AssetsEndpoint
from .base import BaseEndpoint
from .groups import GroupsEndpoint
from .pages import PagesEndpoint
from .users import UsersEndpoint

__all__ = [
    "AssetsEndpoint",
    "BaseEndpoint",
    "GroupsEndpoint",
    "PagesEndpoint",
    "UsersEndpoint",
]
