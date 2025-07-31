"""Page-related data models for wikijs-python-sdk."""

import re
from typing import List, Optional

from pydantic import Field, validator

from .base import BaseModel, TimestampedModel


class Page(TimestampedModel):
    """Represents a Wiki.js page.

    This model contains all the data for a wiki page including
    content, metadata, and computed properties.
    """

    id: int = Field(..., description="Unique page identifier")
    title: str = Field(..., description="Page title")
    path: str = Field(..., description="Page path/slug")
    content: Optional[str] = Field(None, description="Page content")

    # Optional fields that may be present
    description: Optional[str] = Field(None, description="Page description")
    is_published: bool = Field(True, description="Whether page is published")
    is_private: bool = Field(False, description="Whether page is private")

    # Metadata
    tags: List[str] = Field(default_factory=list, description="Page tags")
    locale: str = Field("en", description="Page locale")

    # Author information
    author_id: Optional[int] = Field(None, alias="authorId")
    author_name: Optional[str] = Field(None, alias="authorName")
    author_email: Optional[str] = Field(None, alias="authorEmail")

    # Editor information
    editor: Optional[str] = Field(None, description="Editor used")

    @validator("path")
    def validate_path(cls, v: str) -> str:
        """Validate page path format."""
        if not v:
            raise ValueError("Path cannot be empty")

        # Remove leading/trailing slashes and normalize
        v = v.strip("/")

        # Check for valid characters (letters, numbers, hyphens, underscores, slashes)
        if not re.match(r"^[a-zA-Z0-9\-_/]+$", v):
            raise ValueError("Path contains invalid characters")

        return v

    @validator("title")
    def validate_title(cls, v: str) -> str:
        """Validate page title."""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")

        # Limit title length
        if len(v) > 255:
            raise ValueError("Title cannot exceed 255 characters")

        return v.strip()

    @property
    def word_count(self) -> int:
        """Calculate word count from content."""
        if not self.content:
            return 0

        # Simple word count - split on whitespace
        words = self.content.split()
        return len(words)

    @property
    def reading_time(self) -> int:
        """Estimate reading time in minutes (assuming 200 words per minute)."""
        return max(1, self.word_count // 200)

    @property
    def url_path(self) -> str:
        """Get the full URL path for this page."""
        return f"/{self.path}"

    def extract_headings(self) -> List[str]:
        """Extract markdown headings from content.

        Returns:
            List of heading text (without # markers)
        """
        if not self.content:
            return []

        headings = []
        for line in self.content.split("\n"):
            line = line.strip()
            if line.startswith("#"):
                # Remove # markers and whitespace
                heading = re.sub(r"^#+\s*", "", line).strip()
                if heading:
                    headings.append(heading)

        return headings

    def has_tag(self, tag: str) -> bool:
        """Check if page has a specific tag.

        Args:
            tag: Tag to check for

        Returns:
            True if page has the tag
        """
        return tag.lower() in [t.lower() for t in self.tags]


class PageCreate(BaseModel):
    """Data model for creating a new page."""

    title: str = Field(..., description="Page title")
    path: str = Field(..., description="Page path/slug")
    content: str = Field(..., description="Page content")

    # Optional fields
    description: Optional[str] = Field(None, description="Page description")
    is_published: bool = Field(True, description="Whether to publish immediately")
    is_private: bool = Field(False, description="Whether page should be private")

    tags: List[str] = Field(default_factory=list, description="Page tags")
    locale: str = Field("en", description="Page locale")
    editor: str = Field("markdown", description="Editor to use")

    @validator("path")
    def validate_path(cls, v: str) -> str:
        """Validate page path format."""
        if not v:
            raise ValueError("Path cannot be empty")

        # Remove leading/trailing slashes and normalize
        v = v.strip("/")

        # Check for valid characters
        if not re.match(r"^[a-zA-Z0-9\-_/]+$", v):
            raise ValueError("Path contains invalid characters")

        return v

    @validator("title")
    def validate_title(cls, v: str) -> str:
        """Validate page title."""
        if not v or not v.strip():
            raise ValueError("Title cannot be empty")

        if len(v) > 255:
            raise ValueError("Title cannot exceed 255 characters")

        return v.strip()


class PageUpdate(BaseModel):
    """Data model for updating an existing page."""

    # All fields optional for partial updates
    title: Optional[str] = Field(None, description="Page title")
    content: Optional[str] = Field(None, description="Page content")
    description: Optional[str] = Field(None, description="Page description")

    is_published: Optional[bool] = Field(None, description="Publication status")
    is_private: Optional[bool] = Field(None, description="Privacy status")

    tags: Optional[List[str]] = Field(None, description="Page tags")

    @validator("title")
    def validate_title(cls, v: Optional[str]) -> Optional[str]:
        """Validate page title if provided."""
        if v is not None:
            if not v.strip():
                raise ValueError("Title cannot be empty")

            if len(v) > 255:
                raise ValueError("Title cannot exceed 255 characters")

            return v.strip()

        return v
