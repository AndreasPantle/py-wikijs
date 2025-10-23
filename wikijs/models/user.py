"""User-related data models for wikijs-python-sdk."""

import re
from typing import List, Optional

from pydantic import ConfigDict, EmailStr, Field, field_validator

from .base import BaseModel, TimestampedModel


class UserGroup(BaseModel):
    """Represents a user's group membership.

    This model contains information about a user's membership
    in a specific group.
    """

    id: int = Field(..., description="Group ID")
    name: str = Field(..., description="Group name")


class User(TimestampedModel):
    """Represents a Wiki.js user.

    This model contains all user data including profile information,
    authentication details, and group memberships.
    """

    id: int = Field(..., description="Unique user identifier")
    name: str = Field(..., description="User's full name")
    email: EmailStr = Field(..., description="User's email address")

    # Authentication and status
    provider_key: Optional[str] = Field(None, alias="providerKey", description="Auth provider key")
    is_system: bool = Field(False, alias="isSystem", description="Whether user is system user")
    is_active: bool = Field(True, alias="isActive", description="Whether user is active")
    is_verified: bool = Field(False, alias="isVerified", description="Whether email is verified")

    # Profile information
    location: Optional[str] = Field(None, description="User's location")
    job_title: Optional[str] = Field(None, alias="jobTitle", description="User's job title")
    timezone: Optional[str] = Field(None, description="User's timezone")

    # Permissions and groups
    groups: List[UserGroup] = Field(default_factory=list, description="User's groups")

    # Timestamps handled by TimestampedModel
    last_login_at: Optional[str] = Field(None, alias="lastLoginAt", description="Last login timestamp")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate user name."""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")

        # Check length
        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters long")

        if len(v) > 255:
            raise ValueError("Name cannot exceed 255 characters")

        return v.strip()

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)


class UserCreate(BaseModel):
    """Model for creating a new user.

    This model contains all required and optional fields
    for creating a new Wiki.js user.
    """

    email: EmailStr = Field(..., description="User's email address")
    name: str = Field(..., description="User's full name")
    password_raw: str = Field(..., alias="passwordRaw", description="User's password")

    # Optional fields
    provider_key: str = Field("local", alias="providerKey", description="Auth provider key")
    groups: List[int] = Field(default_factory=list, description="Group IDs to assign")
    must_change_password: bool = Field(False, alias="mustChangePassword", description="Force password change")
    send_welcome_email: bool = Field(True, alias="sendWelcomeEmail", description="Send welcome email")

    # Profile information
    location: Optional[str] = Field(None, description="User's location")
    job_title: Optional[str] = Field(None, alias="jobTitle", description="User's job title")
    timezone: Optional[str] = Field(None, description="User's timezone")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate user name."""
        if not v or not v.strip():
            raise ValueError("Name cannot be empty")

        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters long")

        if len(v) > 255:
            raise ValueError("Name cannot exceed 255 characters")

        return v.strip()

    @field_validator("password_raw")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """Validate password strength."""
        if not v:
            raise ValueError("Password cannot be empty")

        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")

        if len(v) > 255:
            raise ValueError("Password cannot exceed 255 characters")

        return v

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)


class UserUpdate(BaseModel):
    """Model for updating an existing user.

    This model contains optional fields that can be updated
    for an existing Wiki.js user. All fields are optional.
    """

    name: Optional[str] = Field(None, description="User's full name")
    email: Optional[EmailStr] = Field(None, description="User's email address")
    password_raw: Optional[str] = Field(None, alias="passwordRaw", description="New password")

    # Profile information
    location: Optional[str] = Field(None, description="User's location")
    job_title: Optional[str] = Field(None, alias="jobTitle", description="User's job title")
    timezone: Optional[str] = Field(None, description="User's timezone")

    # Group assignments
    groups: Optional[List[int]] = Field(None, description="Group IDs to assign")

    # Status flags
    is_active: Optional[bool] = Field(None, alias="isActive", description="Whether user is active")
    is_verified: Optional[bool] = Field(None, alias="isVerified", description="Whether email is verified")

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate user name if provided."""
        if v is None:
            return v

        if not v.strip():
            raise ValueError("Name cannot be empty")

        if len(v) < 2:
            raise ValueError("Name must be at least 2 characters long")

        if len(v) > 255:
            raise ValueError("Name cannot exceed 255 characters")

        return v.strip()

    @field_validator("password_raw")
    @classmethod
    def validate_password(cls, v: Optional[str]) -> Optional[str]:
        """Validate password strength if provided."""
        if v is None:
            return v

        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters long")

        if len(v) > 255:
            raise ValueError("Password cannot exceed 255 characters")

        return v

    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)
