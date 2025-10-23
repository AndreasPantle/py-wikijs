"""Targeted tests to reach 85% coverage."""

import pytest
import time
from unittest.mock import Mock, patch
from wikijs.cache.memory import MemoryCache
from wikijs.ratelimit import RateLimiter
from wikijs.metrics import MetricsCollector
from wikijs.client import WikiJSClient
from wikijs.exceptions import AuthenticationError, APIError


class TestCacheEdgeCases:
    """Test cache edge cases to cover missing lines."""

    def test_invalidate_resource_with_malformed_keys(self):
        """Test invalidate_resource with malformed cache keys (covers line 132)."""
        cache = MemoryCache(ttl=300)

        # Add some normal keys
        cache._cache["page:123"] = ({"data": "test1"}, time.time() + 300)
        cache._cache["page:456"] = ({"data": "test2"}, time.time() + 300)

        # Add a malformed key without colon separator (covers line 132)
        cache._cache["malformedkey"] = ({"data": "test3"}, time.time() + 300)

        # Invalidate page type - should skip malformed key
        cache.invalidate_resource("page")

        # Normal keys should be gone
        assert "page:123" not in cache._cache
        assert "page:456" not in cache._cache

        # Malformed key should still exist (was skipped by continue on line 132)
        assert "malformedkey" in cache._cache


class TestMetricsEdgeCases:
    """Test metrics edge cases."""

    def test_record_request_with_server_error(self):
        """Test recording request with 5xx status code (covers line 64)."""
        collector = MetricsCollector()

        # Record a server error (5xx)
        collector.record_request(
            endpoint="/test",
            method="GET",
            status_code=500,
            duration_ms=150.0,
            error="Internal Server Error"
        )

        # Check counters
        assert collector._counters["total_requests"] == 1
        assert collector._counters["total_errors"] == 1
        assert collector._counters["total_server_errors"] == 1  # Line 64

    def test_percentile_with_empty_data(self):
        """Test _percentile with empty data (covers line 135)."""
        collector = MetricsCollector()

        # Get percentile with no recorded requests
        result = collector._percentile([], 95)

        # Should return 0.0 for empty data (line 135)
        assert result == 0.0


class TestClientErrorHandling:
    """Test client error handling paths."""

    @patch('wikijs.client.requests.Session')
    def test_connection_unexpected_format(self, mock_session_class):
        """Test test_connection with unexpected response format (covers line 287)."""
        mock_session = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"unexpected": "format"}
        mock_session.request.return_value = mock_response
        mock_session_class.return_value = mock_session

        client = WikiJSClient("https://wiki.example.com", auth="test-key")

        with pytest.raises(APIError, match="Unexpected response format"):
            client.test_connection()

    @patch('wikijs.client.requests.Session')
    def test_connection_reraises_auth_error(self, mock_session_class):
        """Test test_connection re-raises AuthenticationError (covers line 295)."""
        mock_session = Mock()

        def raise_auth_error(*args, **kwargs):
            raise AuthenticationError("Auth failed")

        mock_session.request.side_effect = raise_auth_error
        mock_session_class.return_value = mock_session

        client = WikiJSClient("https://wiki.example.com", auth="test-key")

        with pytest.raises(AuthenticationError, match="Auth failed"):
            client.test_connection()

    @patch('wikijs.client.requests.Session')
    def test_connection_reraises_api_error(self, mock_session_class):
        """Test test_connection re-raises APIError (covers line 307)."""
        mock_session = Mock()

        def raise_api_error(*args, **kwargs):
            raise APIError("API failed")

        mock_session.request.side_effect = raise_api_error
        mock_session_class.return_value = mock_session

        client = WikiJSClient("https://wiki.example.com", auth="test-key")

        with pytest.raises(APIError, match="API failed"):
            client.test_connection()


class TestLoggingEdgeCases:
    """Test logging edge cases."""

    def test_setup_logging_with_json_format(self):
        """Test setup_logging with JSON format."""
        from wikijs.logging import setup_logging

        logger = setup_logging(level="DEBUG", format_type="json")
        assert logger.level == 10  # DEBUG = 10

    def test_json_formatter_with_exception_info(self):
        """Test JSON formatter with exception info (covers line 33)."""
        import logging
        import sys
        from wikijs.logging import JSONFormatter

        formatter = JSONFormatter()

        # Create a log record with actual exception info
        try:
            1 / 0
        except ZeroDivisionError:
            exc_info = sys.exc_info()

        record = logging.LogRecord(
            name="test",
            level=logging.ERROR,
            pathname="test.py",
            lineno=1,
            msg="Error occurred",
            args=(),
            exc_info=exc_info
        )

        result = formatter.format(record)
        assert "exception" in result
        assert "ZeroDivisionError" in result

    def test_json_formatter_with_extra_fields(self):
        """Test JSON formatter with extra fields (covers line 37)."""
        import logging
        from wikijs.logging import JSONFormatter

        formatter = JSONFormatter()

        record = logging.LogRecord(
            name="test",
            level=logging.INFO,
            pathname="test.py",
            lineno=1,
            msg="Test message",
            args=(),
            exc_info=None
        )

        # Add extra attribute
        record.extra = {"user_id": 123, "request_id": "abc"}

        result = formatter.format(record)
        assert "user_id" in result
        assert "123" in result

    def test_setup_logging_with_file_output(self):
        """Test setup_logging with file output (covers line 65)."""
        import tempfile
        import os
        from wikijs.logging import setup_logging

        # Create temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.log') as f:
            log_file = f.name

        try:
            logger = setup_logging(level="INFO", format_type="text", output_file=log_file)
            logger.info("Test message")

            # Verify file was created and has content
            assert os.path.exists(log_file)
            with open(log_file, 'r') as f:
                content = f.read()
                assert "Test message" in content
        finally:
            if os.path.exists(log_file):
                os.unlink(log_file)
