"""Tests for rate limiting functionality."""
import time
import pytest
from wikijs.ratelimit import RateLimiter, PerEndpointRateLimiter


def test_rate_limiter_init():
    """Test rate limiter initialization."""
    limiter = RateLimiter(requests_per_second=10.0)

    assert limiter.rate == 10.0
    assert limiter.burst == 10


def test_rate_limiter_acquire():
    """Test acquiring tokens."""
    limiter = RateLimiter(requests_per_second=100.0)

    # Should be able to acquire immediately
    assert limiter.acquire(timeout=1.0) is True


def test_rate_limiter_burst():
    """Test burst behavior."""
    limiter = RateLimiter(requests_per_second=10.0, burst=5)

    # Should be able to acquire up to burst size
    for _ in range(5):
        assert limiter.acquire(timeout=0.1) is True


def test_rate_limiter_timeout():
    """Test timeout behavior."""
    limiter = RateLimiter(requests_per_second=1.0)

    # Exhaust tokens
    assert limiter.acquire(timeout=1.0) is True

    # Next acquire should timeout quickly
    assert limiter.acquire(timeout=0.1) is False


def test_rate_limiter_reset():
    """Test rate limiter reset."""
    limiter = RateLimiter(requests_per_second=1.0)

    # Exhaust tokens
    limiter.acquire()

    # Reset
    limiter.reset()

    # Should be able to acquire again
    assert limiter.acquire(timeout=0.1) is True


def test_per_endpoint_rate_limiter():
    """Test per-endpoint rate limiting."""
    limiter = PerEndpointRateLimiter(default_rate=10.0)

    # Set different rate for specific endpoint
    limiter.set_limit("/api/special", 5.0)

    # Should use endpoint-specific rate
    assert limiter.acquire("/api/special", timeout=1.0) is True


def test_per_endpoint_default_rate():
    """Test default rate for endpoints."""
    limiter = PerEndpointRateLimiter(default_rate=100.0)

    # Should use default rate for unknown endpoint
    assert limiter.acquire("/api/unknown", timeout=1.0) is True
