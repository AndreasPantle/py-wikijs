"""Tests for User data models."""

import pytest
from pydantic import ValidationError

from wikijs.models import User, UserCreate, UserGroup, UserUpdate


class TestUserGroup:
    """Test UserGroup model."""

    def test_user_group_creation(self):
        """Test creating a valid user group."""
        group = UserGroup(id=1, name="Administrators")
        assert group.id == 1
        assert group.name == "Administrators"

    def test_user_group_required_fields(self):
        """Test that required fields are enforced."""
        with pytest.raises(ValidationError) as exc_info:
            UserGroup(id=1)
        assert "name" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            UserGroup(name="Administrators")
        assert "id" in str(exc_info.value)


class TestUser:
    """Test User model."""

    def test_user_creation_minimal(self):
        """Test creating a user with minimal required fields."""
        user = User(
            id=1,
            name="John Doe",
            email="john@example.com",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        assert user.id == 1
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.is_active is True
        assert user.is_system is False
        assert user.is_verified is False
        assert user.groups == []

    def test_user_creation_full(self):
        """Test creating a user with all fields."""
        groups = [
            UserGroup(id=1, name="Administrators"),
            UserGroup(id=2, name="Editors"),
        ]
        user = User(
            id=1,
            name="John Doe",
            email="john@example.com",
            provider_key="local",
            is_system=False,
            is_active=True,
            is_verified=True,
            location="New York",
            job_title="Senior Developer",
            timezone="America/New_York",
            groups=groups,
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
            last_login_at="2024-01-15T12:00:00Z",
        )
        assert user.id == 1
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.provider_key == "local"
        assert user.is_system is False
        assert user.is_active is True
        assert user.is_verified is True
        assert user.location == "New York"
        assert user.job_title == "Senior Developer"
        assert user.timezone == "America/New_York"
        assert len(user.groups) == 2
        assert user.groups[0].name == "Administrators"
        assert user.last_login_at == "2024-01-15T12:00:00Z"

    def test_user_camel_case_alias(self):
        """Test that camelCase aliases work."""
        user = User(
            id=1,
            name="John Doe",
            email="john@example.com",
            providerKey="local",
            isSystem=False,
            isActive=True,
            isVerified=True,
            jobTitle="Developer",
            createdAt="2024-01-01T00:00:00Z",
            updatedAt="2024-01-01T00:00:00Z",
            lastLoginAt="2024-01-15T12:00:00Z",
        )
        assert user.provider_key == "local"
        assert user.is_system is False
        assert user.is_active is True
        assert user.is_verified is True
        assert user.job_title == "Developer"
        assert user.last_login_at == "2024-01-15T12:00:00Z"

    def test_user_required_fields(self):
        """Test that required fields are enforced."""
        with pytest.raises(ValidationError) as exc_info:
            User(name="John Doe", email="john@example.com")
        assert "id" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            User(id=1, email="john@example.com")
        assert "name" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            User(id=1, name="John Doe")
        assert "email" in str(exc_info.value)

    def test_user_email_validation(self):
        """Test email validation."""
        # Valid email
        user = User(
            id=1,
            name="John Doe",
            email="john@example.com",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        assert user.email == "john@example.com"

        # Invalid email
        with pytest.raises(ValidationError) as exc_info:
            User(
                id=1,
                name="John Doe",
                email="not-an-email",
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
            )
        assert "email" in str(exc_info.value).lower()

    def test_user_name_validation(self):
        """Test name validation."""
        # Too short
        with pytest.raises(ValidationError) as exc_info:
            User(
                id=1,
                name="J",
                email="john@example.com",
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
            )
        assert "at least 2 characters" in str(exc_info.value)

        # Too long
        with pytest.raises(ValidationError) as exc_info:
            User(
                id=1,
                name="x" * 256,
                email="john@example.com",
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
            )
        assert "cannot exceed 255 characters" in str(exc_info.value)

        # Empty
        with pytest.raises(ValidationError) as exc_info:
            User(
                id=1,
                name="",
                email="john@example.com",
                created_at="2024-01-01T00:00:00Z",
                updated_at="2024-01-01T00:00:00Z",
            )
        assert "cannot be empty" in str(exc_info.value)

        # Whitespace trimming
        user = User(
            id=1,
            name="  John Doe  ",
            email="john@example.com",
            created_at="2024-01-01T00:00:00Z",
            updated_at="2024-01-01T00:00:00Z",
        )
        assert user.name == "John Doe"


class TestUserCreate:
    """Test UserCreate model."""

    def test_user_create_minimal(self):
        """Test creating user with minimal required fields."""
        user_data = UserCreate(
            email="john@example.com", name="John Doe", password_raw="secret123"
        )
        assert user_data.email == "john@example.com"
        assert user_data.name == "John Doe"
        assert user_data.password_raw == "secret123"
        assert user_data.provider_key == "local"
        assert user_data.groups == []
        assert user_data.must_change_password is False
        assert user_data.send_welcome_email is True

    def test_user_create_full(self):
        """Test creating user with all fields."""
        user_data = UserCreate(
            email="john@example.com",
            name="John Doe",
            password_raw="secret123",
            provider_key="ldap",
            groups=[1, 2, 3],
            must_change_password=True,
            send_welcome_email=False,
            location="New York",
            job_title="Developer",
            timezone="America/New_York",
        )
        assert user_data.email == "john@example.com"
        assert user_data.name == "John Doe"
        assert user_data.password_raw == "secret123"
        assert user_data.provider_key == "ldap"
        assert user_data.groups == [1, 2, 3]
        assert user_data.must_change_password is True
        assert user_data.send_welcome_email is False
        assert user_data.location == "New York"
        assert user_data.job_title == "Developer"
        assert user_data.timezone == "America/New_York"

    def test_user_create_camel_case_alias(self):
        """Test that camelCase aliases work."""
        user_data = UserCreate(
            email="john@example.com",
            name="John Doe",
            passwordRaw="secret123",
            providerKey="ldap",
            mustChangePassword=True,
            sendWelcomeEmail=False,
            jobTitle="Developer",
        )
        assert user_data.password_raw == "secret123"
        assert user_data.provider_key == "ldap"
        assert user_data.must_change_password is True
        assert user_data.send_welcome_email is False
        assert user_data.job_title == "Developer"

    def test_user_create_required_fields(self):
        """Test that required fields are enforced."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(name="John Doe", password_raw="secret123")
        assert "email" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="john@example.com", password_raw="secret123")
        assert "name" in str(exc_info.value)

        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="john@example.com", name="John Doe")
        # Pydantic uses the field alias in error messages
        assert "passwordRaw" in str(exc_info.value) or "password_raw" in str(
            exc_info.value
        )

    def test_user_create_email_validation(self):
        """Test email validation."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="not-an-email", name="John Doe", password_raw="secret123")
        assert "email" in str(exc_info.value).lower()

    def test_user_create_name_validation(self):
        """Test name validation."""
        # Too short
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="john@example.com", name="J", password_raw="secret123")
        assert "at least 2 characters" in str(exc_info.value)

        # Too long
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="john@example.com", name="x" * 256, password_raw="secret123"
            )
        assert "cannot exceed 255 characters" in str(exc_info.value)

        # Empty
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="john@example.com", name="", password_raw="secret123")
        assert "cannot be empty" in str(exc_info.value)

    def test_user_create_password_validation(self):
        """Test password validation."""
        # Too short
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="john@example.com", name="John Doe", password_raw="123")
        assert "at least 6 characters" in str(exc_info.value)

        # Too long
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="john@example.com", name="John Doe", password_raw="x" * 256
            )
        assert "cannot exceed 255 characters" in str(exc_info.value)

        # Empty
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(email="john@example.com", name="John Doe", password_raw="")
        assert "cannot be empty" in str(exc_info.value)


class TestUserUpdate:
    """Test UserUpdate model."""

    def test_user_update_all_none(self):
        """Test creating empty update."""
        user_data = UserUpdate()
        assert user_data.name is None
        assert user_data.email is None
        assert user_data.password_raw is None
        assert user_data.location is None
        assert user_data.job_title is None
        assert user_data.timezone is None
        assert user_data.groups is None
        assert user_data.is_active is None
        assert user_data.is_verified is None

    def test_user_update_partial(self):
        """Test partial updates."""
        user_data = UserUpdate(name="Jane Doe", email="jane@example.com")
        assert user_data.name == "Jane Doe"
        assert user_data.email == "jane@example.com"
        assert user_data.password_raw is None
        assert user_data.location is None

    def test_user_update_full(self):
        """Test full update."""
        user_data = UserUpdate(
            name="Jane Doe",
            email="jane@example.com",
            password_raw="newsecret123",
            location="San Francisco",
            job_title="Senior Developer",
            timezone="America/Los_Angeles",
            groups=[1, 2],
            is_active=False,
            is_verified=True,
        )
        assert user_data.name == "Jane Doe"
        assert user_data.email == "jane@example.com"
        assert user_data.password_raw == "newsecret123"
        assert user_data.location == "San Francisco"
        assert user_data.job_title == "Senior Developer"
        assert user_data.timezone == "America/Los_Angeles"
        assert user_data.groups == [1, 2]
        assert user_data.is_active is False
        assert user_data.is_verified is True

    def test_user_update_camel_case_alias(self):
        """Test that camelCase aliases work."""
        user_data = UserUpdate(
            passwordRaw="newsecret123",
            jobTitle="Senior Developer",
            isActive=False,
            isVerified=True,
        )
        assert user_data.password_raw == "newsecret123"
        assert user_data.job_title == "Senior Developer"
        assert user_data.is_active is False
        assert user_data.is_verified is True

    def test_user_update_email_validation(self):
        """Test email validation."""
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(email="not-an-email")
        assert "email" in str(exc_info.value).lower()

    def test_user_update_name_validation(self):
        """Test name validation."""
        # Too short
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(name="J")
        assert "at least 2 characters" in str(exc_info.value)

        # Too long
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(name="x" * 256)
        assert "cannot exceed 255 characters" in str(exc_info.value)

        # Empty
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(name="")
        assert "cannot be empty" in str(exc_info.value)

    def test_user_update_password_validation(self):
        """Test password validation."""
        # Too short
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(password_raw="123")
        assert "at least 6 characters" in str(exc_info.value)

        # Too long
        with pytest.raises(ValidationError) as exc_info:
            UserUpdate(password_raw="x" * 256)
        assert "cannot exceed 255 characters" in str(exc_info.value)
