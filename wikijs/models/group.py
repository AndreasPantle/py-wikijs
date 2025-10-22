"""Data models for Wiki.js groups."""

from typing import List, Optional

from pydantic import Field, field_validator

from .base import BaseModel, TimestampedModel


class GroupPermission(BaseModel):
    """Group permission model."""

    id: str = Field(..., description="Permission identifier")
    name: Optional[str] = Field(None, description="Permission name")

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class GroupPageRule(BaseModel):
    """Group page access rule model."""

    id: str = Field(..., description="Rule identifier")
    path: str = Field(..., description="Page path pattern")
    roles: List[str] = Field(default_factory=list, description="Allowed roles")
    match: str = Field(default="START", description="Match type (START, EXACT, REGEX)")
    deny: bool = Field(default=False, description="Whether this is a deny rule")
    locales: List[str] = Field(default_factory=list, description="Allowed locales")

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class GroupUser(BaseModel):
    """User member of a group (minimal representation)."""

    id: int = Field(..., description="User ID")
    name: str = Field(..., description="User name")
    email: str = Field(..., description="User email")

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class Group(TimestampedModel):
    """Wiki.js group model.

    Represents a complete group with all fields.

    Attributes:
        id: Group ID
        name: Group name
        is_system: Whether this is a system group
        redirect_on_login: Path to redirect to on login
        permissions: List of group permissions
        page_rules: List of page access rules
        users: List of users in this group (only populated in get operations)
        created_at: Creation timestamp
        updated_at: Last update timestamp
    """

    id: int = Field(..., description="Group ID")
    name: str = Field(..., min_length=1, max_length=255, description="Group name")
    is_system: bool = Field(
        default=False, alias="isSystem", description="System group flag"
    )
    redirect_on_login: Optional[str] = Field(
        None, alias="redirectOnLogin", description="Redirect path on login"
    )
    permissions: List[str] = Field(
        default_factory=list, description="Permission identifiers"
    )
    page_rules: List[GroupPageRule] = Field(
        default_factory=list, alias="pageRules", description="Page access rules"
    )
    users: List[GroupUser] = Field(
        default_factory=list, description="Users in this group"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate group name."""
        if not v or not v.strip():
            raise ValueError("Group name cannot be empty")
        if len(v.strip()) < 1:
            raise ValueError("Group name must be at least 1 character")
        if len(v) > 255:
            raise ValueError("Group name cannot exceed 255 characters")
        return v.strip()

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class GroupCreate(BaseModel):
    """Model for creating a new group.

    Attributes:
        name: Group name (required)
        redirect_on_login: Path to redirect to on login
        permissions: List of permission identifiers
        page_rules: List of page access rule configurations
    """

    name: str = Field(..., min_length=1, max_length=255, description="Group name")
    redirect_on_login: Optional[str] = Field(
        None, alias="redirectOnLogin", description="Redirect path on login"
    )
    permissions: List[str] = Field(
        default_factory=list, description="Permission identifiers"
    )
    page_rules: List[dict] = Field(
        default_factory=list, alias="pageRules", description="Page access rules"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate group name."""
        if not v or not v.strip():
            raise ValueError("Group name cannot be empty")
        if len(v.strip()) < 1:
            raise ValueError("Group name must be at least 1 character")
        if len(v) > 255:
            raise ValueError("Group name cannot exceed 255 characters")
        return v.strip()

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class GroupUpdate(BaseModel):
    """Model for updating an existing group.

    All fields are optional to support partial updates.

    Attributes:
        name: Updated group name
        redirect_on_login: Updated redirect path
        permissions: Updated permission list
        page_rules: Updated page access rules
    """

    name: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Group name"
    )
    redirect_on_login: Optional[str] = Field(
        None, alias="redirectOnLogin", description="Redirect path on login"
    )
    permissions: Optional[List[str]] = Field(None, description="Permission identifiers")
    page_rules: Optional[List[dict]] = Field(
        None, alias="pageRules", description="Page access rules"
    )

    @field_validator("name")
    @classmethod
    def validate_name(cls, v: Optional[str]) -> Optional[str]:
        """Validate group name if provided."""
        if v is None:
            return v
        if not v or not v.strip():
            raise ValueError("Group name cannot be empty")
        if len(v.strip()) < 1:
            raise ValueError("Group name must be at least 1 character")
        if len(v) > 255:
            raise ValueError("Group name cannot exceed 255 characters")
        return v.strip()

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class GroupAssignUser(BaseModel):
    """Model for assigning a user to a group.

    Attributes:
        group_id: Group ID
        user_id: User ID
    """

    group_id: int = Field(..., alias="groupId", description="Group ID")
    user_id: int = Field(..., alias="userId", description="User ID")

    class Config:
        """Pydantic configuration."""

        populate_by_name = True


class GroupUnassignUser(BaseModel):
    """Model for removing a user from a group.

    Attributes:
        group_id: Group ID
        user_id: User ID
    """

    group_id: int = Field(..., alias="groupId", description="Group ID")
    user_id: int = Field(..., alias="userId", description="User ID")

    class Config:
        """Pydantic configuration."""

        populate_by_name = True
