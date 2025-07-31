"""Authentication module for wikijs-python-sdk.

This module contains authentication handlers for different
authentication methods supported by Wiki.js.

Supported authentication methods:
- API key authentication (APIKeyAuth)
- JWT token authentication (JWTAuth)
- No authentication for testing (NoAuth)
"""

from .api_key import APIKeyAuth
from .base import AuthHandler, NoAuth
from .jwt import JWTAuth

__all__ = [
    "AuthHandler",
    "NoAuth",
    "APIKeyAuth",
    "JWTAuth",
]
