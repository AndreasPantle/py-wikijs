"""Rate limiting for wikijs-python-sdk."""
import time
import threading
from typing import Optional, Dict


class RateLimiter:
    """Token bucket rate limiter."""

    def __init__(
        self,
        requests_per_second: float = 10.0,
        burst: Optional[int] = None
    ):
        """Initialize rate limiter.

        Args:
            requests_per_second: Maximum requests per second
            burst: Maximum burst size (defaults to requests_per_second)
        """
        self.rate = requests_per_second
        self.burst = burst or int(requests_per_second)
        self._tokens = float(self.burst)
        self._last_update = time.time()
        self._lock = threading.Lock()

    def acquire(self, timeout: Optional[float] = None) -> bool:
        """Acquire permission to make a request.

        Args:
            timeout: Maximum time to wait in seconds (None = wait forever)

        Returns:
            True if acquired, False if timeout
        """
        deadline = time.time() + timeout if timeout else None

        while True:
            with self._lock:
                now = time.time()

                # Refill tokens based on elapsed time
                elapsed = now - self._last_update
                self._tokens = min(
                    self.burst,
                    self._tokens + elapsed * self.rate
                )
                self._last_update = now

                # Check if we have tokens
                if self._tokens >= 1.0:
                    self._tokens -= 1.0
                    return True

                # Calculate wait time
                wait_time = (1.0 - self._tokens) / self.rate

            # Check timeout
            if deadline and time.time() + wait_time > deadline:
                return False

            # Sleep and retry
            time.sleep(min(wait_time, 0.1))

    def reset(self) -> None:
        """Reset rate limiter."""
        with self._lock:
            self._tokens = float(self.burst)
            self._last_update = time.time()


class PerEndpointRateLimiter:
    """Rate limiter with per-endpoint limits."""

    def __init__(self, default_rate: float = 10.0):
        """Initialize per-endpoint rate limiter.

        Args:
            default_rate: Default rate limit for endpoints
        """
        self.default_rate = default_rate
        self._limiters: Dict[str, RateLimiter] = {}
        self._lock = threading.Lock()

    def set_limit(self, endpoint: str, rate: float) -> None:
        """Set rate limit for specific endpoint.

        Args:
            endpoint: The endpoint path
            rate: Requests per second for this endpoint
        """
        with self._lock:
            self._limiters[endpoint] = RateLimiter(rate)

    def acquire(self, endpoint: str, timeout: Optional[float] = None) -> bool:
        """Acquire for specific endpoint.

        Args:
            endpoint: The endpoint path
            timeout: Maximum time to wait

        Returns:
            True if acquired, False if timeout
        """
        with self._lock:
            if endpoint not in self._limiters:
                self._limiters[endpoint] = RateLimiter(self.default_rate)
            limiter = self._limiters[endpoint]

        return limiter.acquire(timeout)
