"""Tests for logging functionality."""
import logging
import json
from wikijs.logging import setup_logging, JSONFormatter


def test_json_formatter():
    """Test JSON log formatting."""
    formatter = JSONFormatter()
    record = logging.LogRecord(
        name="test",
        level=logging.INFO,
        pathname="test.py",
        lineno=10,
        msg="Test message",
        args=(),
        exc_info=None
    )

    output = formatter.format(record)
    log_data = json.loads(output)

    assert log_data["level"] == "INFO"
    assert log_data["message"] == "Test message"
    assert "timestamp" in log_data


def test_setup_logging_json():
    """Test JSON logging setup."""
    logger = setup_logging(level=logging.DEBUG, format_type="json")

    assert logger.level == logging.DEBUG
    assert len(logger.handlers) == 1


def test_setup_logging_text():
    """Test text logging setup."""
    logger = setup_logging(level=logging.INFO, format_type="text")

    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1
