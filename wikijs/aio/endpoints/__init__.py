"""Async endpoint handlers for Wiki.js API."""

from .base import AsyncBaseEndpoint
from .pages import AsyncPagesEndpoint

__all__ = [
    "AsyncBaseEndpoint",
    "AsyncPagesEndpoint",
]
