"""Tests for base model functionality."""

import json
from datetime import datetime

from wikijs.models.base import BaseModel, TimestampedModel


class TestModelForTesting(BaseModel):
    """Test model for testing base functionality."""

    name: str
    value: int = 42
    optional_field: str = None


class TestTimestampedModelForTesting(TimestampedModel):
    """Test model with timestamps."""

    title: str


class TestBaseModel:
    """Test base model functionality."""

    def test_basic_model_creation(self):
        """Test basic model creation."""
        model = TestModelForTesting(name="test", value=100)
        assert model.name == "test"
        assert model.value == 100
        assert model.optional_field is None

    def test_to_dict_basic(self):
        """Test to_dict method."""
        model = TestModelForTesting(name="test", value=100)
        result = model.to_dict()

        expected = {"name": "test", "value": 100}
        assert result == expected

    def test_to_dict_with_none_values(self):
        """Test to_dict with None values."""
        model = TestModelForTesting(name="test", value=100)

        # Test excluding None values (default)
        result_exclude = model.to_dict(exclude_none=True)
        expected_exclude = {"name": "test", "value": 100}
        assert result_exclude == expected_exclude

        # Test including None values
        result_include = model.to_dict(exclude_none=False)
        expected_include = {
            "name": "test",
            "value": 100,
            "optional_field": None,
        }
        assert result_include == expected_include

    def test_to_json_basic(self):
        """Test to_json method."""
        model = TestModelForTesting(name="test", value=100)
        result = model.to_json()

        # Parse the JSON to verify structure
        parsed = json.loads(result)
        expected = {"name": "test", "value": 100}
        assert parsed == expected

    def test_to_json_with_none_values(self):
        """Test to_json with None values."""
        model = TestModelForTesting(name="test", value=100)

        # Test excluding None values (default)
        result_exclude = model.to_json(exclude_none=True)
        parsed_exclude = json.loads(result_exclude)
        expected_exclude = {"name": "test", "value": 100}
        assert parsed_exclude == expected_exclude

        # Test including None values
        result_include = model.to_json(exclude_none=False)
        parsed_include = json.loads(result_include)
        expected_include = {
            "name": "test",
            "value": 100,
            "optional_field": None,
        }
        assert parsed_include == expected_include

    def test_from_dict(self):
        """Test from_dict class method."""
        data = {"name": "test", "value": 200}
        model = TestModelForTesting.from_dict(data)

        assert isinstance(model, TestModelForTesting)
        assert model.name == "test"
        assert model.value == 200

    def test_from_json(self):
        """Test from_json class method."""
        json_str = '{"name": "test", "value": 300}'
        model = TestModelForTesting.from_json(json_str)

        assert isinstance(model, TestModelForTesting)
        assert model.name == "test"
        assert model.value == 300


class TestTimestampedModel:
    """Test timestamped model functionality."""

    def test_timestamped_model_creation(self):
        """Test timestamped model creation."""
        model = TestTimestampedModelForTesting(title="Test Title")
        assert model.title == "Test Title"
        assert model.created_at is None
        assert model.updated_at is None

    def test_timestamped_model_with_timestamps(self):
        """Test timestamped model with timestamps."""
        now = datetime.now()
        model = TestTimestampedModelForTesting(
            title="Test Title", created_at=now, updated_at=now
        )
        assert model.title == "Test Title"
        assert model.created_at == now
        assert model.updated_at == now

    def test_is_new_property_true(self):
        """Test is_new property returns True for new models."""
        model = TestTimestampedModelForTesting(title="Test Title")
        assert model.is_new is True

    def test_is_new_property_false(self):
        """Test is_new property returns False for existing models."""
        now = datetime.now()
        model = TestTimestampedModelForTesting(title="Test Title", created_at=now)
        assert model.is_new is False

    def test_datetime_serialization(self):
        """Test datetime serialization in JSON."""
        now = datetime(2023, 1, 1, 12, 0, 0)
        model = TestTimestampedModelForTesting(
            title="Test Title", created_at=now, updated_at=now
        )

        json_str = model.to_json()
        parsed = json.loads(json_str)

        assert parsed["created_at"] == "2023-01-01T12:00:00"
        assert parsed["updated_at"] == "2023-01-01T12:00:00"
