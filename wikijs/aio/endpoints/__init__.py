"""Async endpoint handlers for Wiki.js API."""

from .assets import AsyncAssetsEndpoint
from .base import AsyncBaseEndpoint
from .groups import AsyncGroupsEndpoint
from .pages import AsyncPagesEndpoint
from .users import AsyncUsersEndpoint

__all__ = [
    "AsyncAssetsEndpoint",
    "AsyncBaseEndpoint",
    "AsyncGroupsEndpoint",
    "AsyncPagesEndpoint",
    "AsyncUsersEndpoint",
]
