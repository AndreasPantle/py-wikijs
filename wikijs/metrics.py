"""Metrics and telemetry for wikijs-python-sdk."""
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from collections import defaultdict
import threading


@dataclass
class RequestMetrics:
    """Metrics for a single request."""
    endpoint: str
    method: str
    status_code: int
    duration_ms: float
    timestamp: float
    error: Optional[str] = None


class MetricsCollector:
    """Collect and aggregate metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        self._lock = threading.Lock()
        self._requests: List[RequestMetrics] = []
        self._counters: Dict[str, int] = defaultdict(int)
        self._gauges: Dict[str, float] = {}
        self._histograms: Dict[str, List[float]] = defaultdict(list)

    def record_request(
        self,
        endpoint: str,
        method: str,
        status_code: int,
        duration_ms: float,
        error: Optional[str] = None
    ) -> None:
        """Record API request metrics.

        Args:
            endpoint: The API endpoint
            method: HTTP method
            status_code: HTTP status code
            duration_ms: Request duration in milliseconds
            error: Optional error message
        """
        with self._lock:
            metric = RequestMetrics(
                endpoint=endpoint,
                method=method,
                status_code=status_code,
                duration_ms=duration_ms,
                timestamp=time.time(),
                error=error
            )
            self._requests.append(metric)

            # Update counters
            self._counters["total_requests"] += 1
            if status_code >= 400:
                self._counters["total_errors"] += 1
            if status_code >= 500:
                self._counters["total_server_errors"] += 1

            # Update histograms
            self._histograms[f"{method}_{endpoint}"].append(duration_ms)

    def increment(self, counter_name: str, value: int = 1) -> None:
        """Increment counter.

        Args:
            counter_name: Name of the counter
            value: Value to increment by
        """
        with self._lock:
            self._counters[counter_name] += value

    def set_gauge(self, gauge_name: str, value: float) -> None:
        """Set gauge value.

        Args:
            gauge_name: Name of the gauge
            value: Value to set
        """
        with self._lock:
            self._gauges[gauge_name] = value

    def get_stats(self) -> Dict:
        """Get aggregated statistics.

        Returns:
            Dictionary of aggregated statistics
        """
        with self._lock:
            total = self._counters.get("total_requests", 0)
            errors = self._counters.get("total_errors", 0)

            stats = {
                "total_requests": total,
                "total_errors": errors,
                "error_rate": (errors / total * 100) if total > 0 else 0,
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
            }

            # Calculate percentiles for latency
            if self._requests:
                durations = [r.duration_ms for r in self._requests]
                durations.sort()

                stats["latency"] = {
                    "min": min(durations),
                    "max": max(durations),
                    "avg": sum(durations) / len(durations),
                    "p50": self._percentile(durations, 50),
                    "p95": self._percentile(durations, 95),
                    "p99": self._percentile(durations, 99),
                }

            return stats

    @staticmethod
    def _percentile(data: List[float], percentile: int) -> float:
        """Calculate percentile.

        Args:
            data: Sorted list of values
            percentile: Percentile to calculate

        Returns:
            Percentile value
        """
        if not data:
            return 0.0
        index = int(len(data) * percentile / 100)
        return data[min(index, len(data) - 1)]

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._requests.clear()
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()


# Global metrics collector
_metrics = MetricsCollector()


def get_metrics() -> MetricsCollector:
    """Get global metrics collector.

    Returns:
        Global MetricsCollector instance
    """
    return _metrics
