"""Tests for metrics functionality."""
from wikijs.metrics import MetricsCollector, get_metrics


def test_metrics_collector_init():
    """Test metrics collector initialization."""
    collector = MetricsCollector()
    stats = collector.get_stats()

    assert stats["total_requests"] == 0
    assert stats["total_errors"] == 0


def test_record_request():
    """Test recording requests."""
    collector = MetricsCollector()

    # Record successful request
    collector.record_request("/api/test", "GET", 200, 100.0)

    stats = collector.get_stats()
    assert stats["total_requests"] == 1
    assert stats["total_errors"] == 0


def test_record_error():
    """Test recording errors."""
    collector = MetricsCollector()

    # Record error request
    collector.record_request("/api/test", "GET", 404, 50.0, error="Not found")

    stats = collector.get_stats()
    assert stats["total_requests"] == 1
    assert stats["total_errors"] == 1


def test_latency_stats():
    """Test latency statistics."""
    collector = MetricsCollector()

    # Record multiple requests
    collector.record_request("/api/test", "GET", 200, 100.0)
    collector.record_request("/api/test", "GET", 200, 200.0)
    collector.record_request("/api/test", "GET", 200, 150.0)

    stats = collector.get_stats()
    assert "latency" in stats
    assert stats["latency"]["min"] == 100.0
    assert stats["latency"]["max"] == 200.0
    assert stats["latency"]["avg"] == 150.0


def test_increment_counter():
    """Test incrementing counters."""
    collector = MetricsCollector()

    collector.increment("custom_counter", 5)
    collector.increment("custom_counter", 3)

    stats = collector.get_stats()
    assert stats["counters"]["custom_counter"] == 8


def test_set_gauge():
    """Test setting gauges."""
    collector = MetricsCollector()

    collector.set_gauge("memory_usage", 75.5)

    stats = collector.get_stats()
    assert stats["gauges"]["memory_usage"] == 75.5


def test_reset_metrics():
    """Test resetting metrics."""
    collector = MetricsCollector()

    collector.record_request("/api/test", "GET", 200, 100.0)
    collector.reset()

    stats = collector.get_stats()
    assert stats["total_requests"] == 0


def test_get_global_metrics():
    """Test getting global metrics instance."""
    metrics = get_metrics()
    assert isinstance(metrics, MetricsCollector)
