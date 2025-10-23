"""Tests for Group data models."""

import pytest
from pydantic import ValidationError

from wikijs.models import Group, GroupCreate, GroupUpdate


class TestGroup:
    """Test Group model."""

    def test_group_creation_minimal(self):
        """Test creating a group with minimal fields."""
        group = Group(
            id=1,
            name="Administrators",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        assert group.id == 1
        assert group.name == "Administrators"
        assert group.is_system is False
        assert group.permissions == []
        assert group.page_rules == []
        assert group.users == []

    def test_group_creation_full(self):
        """Test creating a group with all fields."""
        group = Group(
            id=1,
            name="Editors",
            is_system=False,
            redirect_on_login="/dashboard",
            permissions=["read:pages", "write:pages"],
            page_rules=[
                {"id": "1", "path": "/docs/*", "roles": ["write"], "match": "START"}
            ],
            users=[{"id": 1, "name": "John Doe", "email": "john@example.com"}],
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        assert group.name == "Editors"
        assert group.redirect_on_login == "/dashboard"
        assert len(group.permissions) == 2
        assert len(group.page_rules) == 1
        assert len(group.users) == 1

    def test_group_name_validation(self):
        """Test name validation."""
        # Too short
        with pytest.raises(ValidationError):
            Group(
                id=1,
                name="",
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
            )

        # Too long
        with pytest.raises(ValidationError):
            Group(
                id=1,
                name="x" * 256,
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
            )


class TestGroupCreate:
    """Test GroupCreate model."""

    def test_group_create_minimal(self):
        """Test creating group with minimal fields."""
        group_data = GroupCreate(name="Test Group")
        assert group_data.name == "Test Group"
        assert group_data.permissions == []
        assert group_data.page_rules == []

    def test_group_create_full(self):
        """Test creating group with all fields."""
        group_data = GroupCreate(
            name="Test Group",
            redirect_on_login="/home",
            permissions=["read:pages"],
            page_rules=[{"path": "/*", "roles": ["read"]}],
        )
        assert group_data.redirect_on_login == "/home"
        assert len(group_data.permissions) == 1

    def test_group_create_name_validation(self):
        """Test name validation."""
        with pytest.raises(ValidationError):
            GroupCreate(name="")


class TestGroupUpdate:
    """Test GroupUpdate model."""

    def test_group_update_empty(self):
        """Test empty update."""
        update_data = GroupUpdate()
        assert update_data.name is None
        assert update_data.permissions is None

    def test_group_update_partial(self):
        """Test partial update."""
        update_data = GroupUpdate(name="Updated Name")
        assert update_data.name == "Updated Name"
        assert update_data.permissions is None
