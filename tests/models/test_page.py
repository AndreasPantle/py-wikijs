"""Tests for Page models."""

import pytest

from wikijs.models.page import Page, PageCreate, PageUpdate


class TestPageModel:
    """Test Page model functionality."""

    @pytest.fixture
    def valid_page_data(self):
        """Valid page data for testing."""
        return {
            "id": 123,
            "title": "Test Page",
            "path": "test-page",
            "content": "# Test Page\n\nThis is test content with **bold** and *italic* text.",
            "description": "A test page",
            "is_published": True,
            "is_private": False,
            "tags": ["test", "example"],
            "locale": "en",
            "author_id": 1,
            "author_name": "Test User",
            "author_email": "test@example.com",
            "editor": "markdown",
            "created_at": "2023-01-01T00:00:00Z",
            "updated_at": "2023-01-02T00:00:00Z",
        }

    def test_page_creation_valid(self, valid_page_data):
        """Test creating a valid page."""
        page = Page(**valid_page_data)

        assert page.id == 123
        assert page.title == "Test Page"
        assert page.path == "test-page"
        assert (
            page.content
            == "# Test Page\n\nThis is test content with **bold** and *italic* text."
        )
        assert page.is_published is True
        assert page.tags == ["test", "example"]

    def test_page_creation_minimal(self):
        """Test creating page with minimal required fields."""
        page = Page(
            id=1,
            title="Minimal Page",
            path="minimal",
            content="Content",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
        )

        assert page.id == 1
        assert page.title == "Minimal Page"
        assert page.is_published is True  # Default value
        assert page.tags == []  # Default value

    def test_page_path_validation_valid(self):
        """Test valid path validation."""
        valid_paths = [
            "simple-path",
            "path/with/slashes",
            "path_with_underscores",
            "path123",
            "category/subcategory/page-name",
        ]

        for path in valid_paths:
            page = Page(
                id=1,
                title="Test",
                path=path,
                content="Content",
                created_at="2023-01-01T00:00:00Z",
                updated_at="2023-01-01T00:00:00Z",
            )
            assert page.path == path

    def test_page_path_validation_invalid(self):
        """Test invalid path validation."""
        invalid_paths = [
            "",  # Empty
            "path with spaces",  # Spaces
            "path@with@symbols",  # Special characters
            "path.with.dots",  # Dots
        ]

        for path in invalid_paths:
            with pytest.raises(ValueError):
                Page(
                    id=1,
                    title="Test",
                    path=path,
                    content="Content",
                    created_at="2023-01-01T00:00:00Z",
                    updated_at="2023-01-01T00:00:00Z",
                )

    def test_page_path_normalization(self):
        """Test path normalization."""
        # Leading/trailing slashes should be removed
        page = Page(
            id=1,
            title="Test",
            path="/path/to/page/",
            content="Content",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
        )
        assert page.path == "path/to/page"

    def test_page_title_validation_valid(self):
        """Test valid title validation."""
        page = Page(
            id=1,
            title="  Valid Title with Spaces  ",  # Should be trimmed
            path="test",
            content="Content",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
        )
        assert page.title == "Valid Title with Spaces"

    def test_page_title_validation_invalid(self):
        """Test invalid title validation."""
        invalid_titles = [
            "",  # Empty
            "   ",  # Only whitespace
            "x" * 256,  # Too long
        ]

        for title in invalid_titles:
            with pytest.raises(ValueError):
                Page(
                    id=1,
                    title=title,
                    path="test",
                    content="Content",
                    created_at="2023-01-01T00:00:00Z",
                    updated_at="2023-01-01T00:00:00Z",
                )

    def test_page_word_count(self, valid_page_data):
        """Test word count calculation."""
        page = Page(**valid_page_data)
        # "# Test Page\n\nThis is test content with **bold** and *italic* text."
        # Words: Test, Page, This, is, test, content, with, bold, and, italic, text
        assert page.word_count == 12

    def test_page_word_count_empty_content(self):
        """Test word count with empty content."""
        page = Page(
            id=1,
            title="Test",
            path="test",
            content="",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
        )
        assert page.word_count == 0

    def test_page_reading_time(self, valid_page_data):
        """Test reading time calculation."""
        page = Page(**valid_page_data)
        # 11 words, assuming 200 words per minute, should be 1 minute (minimum)
        assert page.reading_time == 1

    def test_page_reading_time_long_content(self):
        """Test reading time with long content."""
        long_content = " ".join(["word"] * 500)  # 500 words
        page = Page(
            id=1,
            title="Test",
            path="test",
            content=long_content,
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
        )
        # 500 words / 200 words per minute = 2.5, rounded down to 2
        assert page.reading_time == 2

    def test_page_url_path(self, valid_page_data):
        """Test URL path generation."""
        page = Page(**valid_page_data)
        assert page.url_path == "/test-page"

    def test_page_extract_headings(self):
        """Test heading extraction from markdown content."""
        content = """# Main Title

Some content here.

## Secondary Heading

More content.

### Third Level

And more content.

## Another Secondary

Final content."""

        page = Page(
            id=1,
            title="Test",
            path="test",
            content=content,
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
        )

        headings = page.extract_headings()
        expected = [
            "Main Title",
            "Secondary Heading",
            "Third Level",
            "Another Secondary",
        ]
        assert headings == expected

    def test_page_extract_headings_empty_content(self):
        """Test heading extraction with no content."""
        page = Page(
            id=1,
            title="Test",
            path="test",
            content="",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
        )
        assert page.extract_headings() == []

    def test_page_has_tag(self, valid_page_data):
        """Test tag checking."""
        page = Page(**valid_page_data)

        assert page.has_tag("test") is True
        assert page.has_tag("example") is True
        assert page.has_tag("TEST") is True  # Case insensitive
        assert page.has_tag("nonexistent") is False

    def test_page_has_tag_no_tags(self):
        """Test tag checking with no tags."""
        page = Page(
            id=1,
            title="Test",
            path="test",
            content="Content",
            created_at="2023-01-01T00:00:00Z",
            updated_at="2023-01-01T00:00:00Z",
        )
        assert page.has_tag("any") is False


class TestPageCreateModel:
    """Test PageCreate model functionality."""

    def test_page_create_valid(self):
        """Test creating valid PageCreate."""
        page_create = PageCreate(
            title="New Page",
            path="new-page",
            content="# New Page\n\nContent here.",
        )

        assert page_create.title == "New Page"
        assert page_create.path == "new-page"
        assert page_create.content == "# New Page\n\nContent here."
        assert page_create.is_published is True  # Default
        assert page_create.editor == "markdown"  # Default

    def test_page_create_with_optional_fields(self):
        """Test PageCreate with optional fields."""
        page_create = PageCreate(
            title="New Page",
            path="new-page",
            content="Content",
            description="A new page",
            is_published=False,
            is_private=True,
            tags=["new", "test"],
            locale="fr",
            editor="html",
        )

        assert page_create.description == "A new page"
        assert page_create.is_published is False
        assert page_create.is_private is True
        assert page_create.tags == ["new", "test"]
        assert page_create.locale == "fr"
        assert page_create.editor == "html"

    def test_page_create_path_validation(self):
        """Test path validation in PageCreate."""
        # Valid path
        PageCreate(title="Test", path="valid-path", content="Content")

        # Invalid paths should raise errors
        with pytest.raises(ValueError):
            PageCreate(title="Test", path="", content="Content")

        with pytest.raises(ValueError):
            PageCreate(title="Test", path="invalid path", content="Content")

    def test_page_create_title_validation(self):
        """Test title validation in PageCreate."""
        # Valid title
        PageCreate(title="Valid Title", path="test", content="Content")

        # Invalid titles should raise errors
        with pytest.raises(ValueError):
            PageCreate(title="", path="test", content="Content")

        with pytest.raises(ValueError):
            PageCreate(title="x" * 256, path="test", content="Content")


class TestPageUpdateModel:
    """Test PageUpdate model functionality."""

    def test_page_update_empty(self):
        """Test creating empty PageUpdate."""
        page_update = PageUpdate()

        assert page_update.title is None
        assert page_update.content is None
        assert page_update.description is None
        assert page_update.is_published is None
        assert page_update.tags is None

    def test_page_update_partial(self):
        """Test partial PageUpdate."""
        page_update = PageUpdate(title="Updated Title", content="Updated content")

        assert page_update.title == "Updated Title"
        assert page_update.content == "Updated content"
        assert page_update.description is None  # Not updated

    def test_page_update_full(self):
        """Test full PageUpdate."""
        page_update = PageUpdate(
            title="Updated Title",
            content="Updated content",
            description="Updated description",
            is_published=False,
            is_private=True,
            tags=["updated", "test"],
        )

        assert page_update.title == "Updated Title"
        assert page_update.content == "Updated content"
        assert page_update.description == "Updated description"
        assert page_update.is_published is False
        assert page_update.is_private is True
        assert page_update.tags == ["updated", "test"]

    def test_page_update_title_validation(self):
        """Test title validation in PageUpdate."""
        # Valid title
        PageUpdate(title="Valid Title")

        # None should be allowed (no update)
        PageUpdate(title=None)

        # Invalid titles should raise errors
        with pytest.raises(ValueError):
            PageUpdate(title="")

        with pytest.raises(ValueError):
            PageUpdate(title="x" * 256)
