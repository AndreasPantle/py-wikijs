"""API endpoints module for wikijs-python-sdk.

This module contains endpoint handlers for different
Wiki.js API endpoints.

Implemented:
- Pages API (CRUD operations) ✅
- Users API (user management) ✅

Future implementations:
- Groups API (group management)
- Assets API (file management)
- System API (system information)
"""

from .base import BaseEndpoint
from .pages import PagesEndpoint
from .users import UsersEndpoint

__all__ = [
    "BaseEndpoint",
    "PagesEndpoint",
    "UsersEndpoint",
]
