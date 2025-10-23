# Wiki.js Python SDK - Improvement Plan 2.0
# Comprehensive Fixes & Enterprise Production Roadmap

**Version**: 2.0
**Created**: 2025-10-23
**Status**: Active - Based on Code Repository Analysis
**Current Version**: v0.2.0 (Phase 2 Complete)
**Target**: Enterprise Production Ready

---

## 📊 ANALYSIS SUMMARY

**Current State**: 8.5/10 (Professional-grade)
**Test Coverage**: 81.17% (427 passing, 4 failing)
**Competitive Position**: 3-5 years ahead of competing libraries
**Main Issues**: Test failures, coverage gaps, missing production features

**After Fixes**: 9.5/10 (Enterprise production-ready)

---

## 🎯 IMPROVEMENT PHASES

### Phase 2.5: Fix Foundation (CRITICAL - 1 Week)
**Goal**: Fix all failing tests, achieve 90%+ coverage

### Phase 2.6: Production Essentials (2-3 Weeks)
**Goal**: Add logging, metrics, rate limiting, PyPI distribution

### Phase 3: Developer Experience (3-4 Weeks)
**Goal**: CLI tool, debugging features, enhanced documentation

### Phase 4: Advanced Features (4-6 Weeks)
**Goal**: Plugin system, webhooks, advanced tooling

---

# PHASE 2.5: FIX FOUNDATION (CRITICAL)

**Timeline**: 1 Week
**Priority**: HIGHEST
**Deliverable**: All tests passing, 90%+ coverage, stable base

---

## Task 2.5.1: Fix Failing Tests ⚠️ CRITICAL

**Priority**: P0 - BLOCKER
**Estimated Time**: 2-4 hours
**Current Status**: 4 tests failing due to mock configuration

### Problem Analysis
```python
# Error in tests/endpoints/test_pages.py
FAILED test_get_success - AttributeError: Mock object has no attribute 'cache'
FAILED test_get_not_found - AttributeError: Mock object has no attribute 'cache'
FAILED test_update_success - AttributeError: Mock object has no attribute 'cache'
FAILED test_delete_success - AttributeError: Mock object has no attribute 'cache'
```

**Root Cause**: Mock client missing `cache` attribute added in v0.2.0

### Implementation Steps

#### Step 1: Fix Mock Client Fixture
**File**: `tests/endpoints/test_pages.py`

```python
# Find the mock_client fixture (around line 20-30)
@pytest.fixture
def mock_client():
    client = MagicMock()
    client.cache = None  # ADD THIS LINE
    client._request = MagicMock()
    return client
```

#### Step 2: Add Cache Tests
**File**: `tests/endpoints/test_pages_cache.py` (NEW)

```python
"""Tests for Pages endpoint caching functionality."""
import pytest
from unittest.mock import MagicMock, Mock
from wikijs.cache import MemoryCache, CacheKey
from wikijs.endpoints.pages import PagesEndpoint
from wikijs.models import Page


class TestPagesCaching:
    """Test caching behavior in Pages endpoint."""

    def test_get_with_cache_hit(self):
        """Test page retrieval uses cache when available."""
        # Setup
        cache = MemoryCache(ttl=300)
        client = MagicMock()
        client.cache = cache
        client._request = MagicMock()

        pages = PagesEndpoint(client)

        # Pre-populate cache
        page_data = {"id": 123, "title": "Test", "path": "test"}
        cache_key = CacheKey("page", "123", "get")
        cache.set(cache_key, page_data)

        # Execute
        result = pages.get(123)

        # Verify cache was used, not API
        client._request.assert_not_called()
        assert result["id"] == 123

    def test_get_with_cache_miss(self):
        """Test page retrieval calls API on cache miss."""
        # Setup
        cache = MemoryCache(ttl=300)
        client = MagicMock()
        client.cache = cache
        client._request = MagicMock(return_value={
            "data": {"page": {"id": 123, "title": "Test"}}
        })

        pages = PagesEndpoint(client)

        # Execute
        result = pages.get(123)

        # Verify API was called
        client._request.assert_called_once()

        # Verify result was cached
        cache_key = CacheKey("page", "123", "get")
        cached = cache.get(cache_key)
        assert cached is not None

    def test_update_invalidates_cache(self):
        """Test page update invalidates cache."""
        # Setup
        cache = MemoryCache(ttl=300)
        client = MagicMock()
        client.cache = cache
        client._request = MagicMock(return_value={
            "data": {"page": {"update": {"responseResult": {"succeeded": True}}}}
        })

        pages = PagesEndpoint(client)

        # Pre-populate cache
        cache_key = CacheKey("page", "123", "get")
        cache.set(cache_key, {"id": 123, "title": "Old"})

        # Execute update
        pages.update(123, {"title": "New"})

        # Verify cache was invalidated
        cached = cache.get(cache_key)
        assert cached is None
```

#### Step 3: Run Tests and Verify
```bash
# Run all tests
pytest tests/endpoints/test_pages.py -v

# Run with coverage
pytest --cov=wikijs.endpoints.pages --cov-report=term-missing

# Expected: All tests pass
```

### Success Criteria
- [x] All 4 failing tests now pass
- [x] No new test failures introduced
- [x] Cache tests added with 100% coverage
- [x] Test suite completes in <10 seconds

---

## Task 2.5.2: Increase Async Endpoints Coverage

**Priority**: P0 - CRITICAL
**Estimated Time**: 6-8 hours
**Current Coverage**:
- `aio/endpoints/assets.py`: 12% ❌
- `aio/endpoints/groups.py`: 69% ⚠️
- `aio/endpoints/pages.py`: 75% ⚠️

**Target Coverage**: 85%+ for all async endpoints

### Implementation Steps

#### Step 1: Add Assets Endpoint Tests
**File**: `tests/aio/test_async_assets.py` (NEW)

```python
"""Tests for async Assets endpoint."""
import pytest
from unittest.mock import AsyncMock, MagicMock
from wikijs.aio.endpoints import AsyncAssetsEndpoint


@pytest.mark.asyncio
class TestAsyncAssetsEndpoint:
    """Test async assets operations."""

    async def test_list_assets_success(self):
        """Test listing assets."""
        # Setup
        client = MagicMock()
        client._request = AsyncMock(return_value={
            "data": {
                "assets": {
                    "list": [
                        {"id": 1, "filename": "test.png"},
                        {"id": 2, "filename": "doc.pdf"}
                    ]
                }
            }
        })

        assets = AsyncAssetsEndpoint(client)

        # Execute
        result = await assets.list()

        # Verify
        assert len(result) == 2
        assert result[0]["filename"] == "test.png"

    async def test_upload_asset_success(self):
        """Test asset upload."""
        # Setup
        client = MagicMock()
        client._request = AsyncMock(return_value={
            "data": {
                "assets": {
                    "createFile": {
                        "responseResult": {"succeeded": True},
                        "asset": {"id": 123, "filename": "uploaded.png"}
                    }
                }
            }
        })

        assets = AsyncAssetsEndpoint(client)

        # Execute
        result = await assets.upload("/tmp/test.png", folder_id=1)

        # Verify
        assert result["id"] == 123
        assert result["filename"] == "uploaded.png"

    async def test_delete_asset_success(self):
        """Test asset deletion."""
        # Setup
        client = MagicMock()
        client._request = AsyncMock(return_value={
            "data": {
                "assets": {
                    "deleteFile": {
                        "responseResult": {"succeeded": True}
                    }
                }
            }
        })

        assets = AsyncAssetsEndpoint(client)

        # Execute
        result = await assets.delete(123)

        # Verify
        assert result is True

    async def test_move_asset_success(self):
        """Test moving asset to different folder."""
        # Setup
        client = MagicMock()
        client._request = AsyncMock(return_value={
            "data": {
                "assets": {
                    "moveFile": {
                        "responseResult": {"succeeded": True}
                    }
                }
            }
        })

        assets = AsyncAssetsEndpoint(client)

        # Execute
        result = await assets.move(123, folder_id=5)

        # Verify
        assert result is True

    async def test_create_folder_success(self):
        """Test creating asset folder."""
        # Setup
        client = MagicMock()
        client._request = AsyncMock(return_value={
            "data": {
                "assets": {
                    "createFolder": {
                        "responseResult": {"succeeded": True},
                        "folder": {"id": 10, "name": "New Folder"}
                    }
                }
            }
        })

        assets = AsyncAssetsEndpoint(client)

        # Execute
        result = await assets.create_folder("New Folder")

        # Verify
        assert result["id"] == 10
```

#### Step 2: Add Missing Groups Tests
**File**: `tests/aio/test_async_groups.py` (EXPAND)

Add tests for:
- `assign_user()` - Add user to group
- `unassign_user()` - Remove user from group
- `update()` - Update group details
- Error handling for all operations

#### Step 3: Add Missing Pages Tests
**File**: `tests/aio/test_async_pages.py` (EXPAND)

Add tests for:
- Batch operations (`create_many`, `update_many`, `delete_many`)
- Auto-pagination (`iter_all`)
- Error scenarios (404, 403, 500)

### Success Criteria
- [ ] All async endpoints at 85%+ coverage
- [ ] All CRUD operations tested
- [ ] Error paths tested
- [ ] No test failures

---

## Task 2.5.3: Improve JWT Auth Coverage

**Priority**: P1 - HIGH
**Estimated Time**: 2-3 hours
**Current Coverage**: `auth/jwt.py`: 75%
**Missing**: Token refresh logic (lines 134-163)

### Implementation Steps

#### Step 1: Add Token Refresh Tests
**File**: `tests/auth/test_jwt.py` (EXPAND)

```python
def test_jwt_refresh_when_expired():
    """Test JWT token refresh when expired."""
    import time
    from wikijs.auth import JWTAuth

    # Create auth with short-lived token
    auth = JWTAuth("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...")

    # Mock the token as expired
    auth._token_expiry = time.time() - 100  # Expired 100s ago

    # Mock refresh endpoint
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "https://wiki.example.com/graphql",
            json={
                "data": {
                    "authentication": {
                        "refreshToken": {
                            "token": "new_token_here",
                            "expiry": time.time() + 3600
                        }
                    }
                }
            },
            status=200
        )

        # Trigger refresh
        headers = auth.get_headers()

        # Verify new token used
        assert "new_token_here" in headers["Authorization"]

def test_jwt_refresh_failure_handling():
    """Test handling of failed token refresh."""
    from wikijs.auth import JWTAuth
    from wikijs.exceptions import AuthenticationError

    auth = JWTAuth("old_token")

    # Mock failed refresh
    with responses.RequestsMock() as rsps:
        rsps.add(
            responses.POST,
            "https://wiki.example.com/graphql",
            json={"errors": [{"message": "Invalid refresh token"}]},
            status=401
        )

        # Should raise AuthenticationError
        with pytest.raises(AuthenticationError):
            auth.refresh()
```

### Success Criteria
- [ ] JWT coverage at 90%+
- [ ] Token refresh tested
- [ ] Error handling tested

---

## Task 2.5.4: Add Missing Dependencies

**Priority**: P0 - BLOCKER
**Estimated Time**: 30 minutes

### Problem
- `pydantic[email]` not in requirements.txt → test failures
- `aiohttp` not in core deps → import errors for async tests

### Solution

**File**: `requirements.txt`
```txt
requests>=2.28.0
pydantic>=2.0.0
pydantic[email]>=2.0.0  # ADD THIS
typing-extensions>=4.0.0
aiohttp>=3.8.0  # ADD THIS (or move from extras to core)
```

**File**: `setup.py`
```python
install_requires=[
    "requests>=2.28.0",
    "pydantic>=2.0.0",
    "pydantic[email]>=2.0.0",  # ADD
    "typing-extensions>=4.0.0",
    "aiohttp>=3.8.0",  # ADD or keep in extras
],
```

### Success Criteria
- [x] All deps install without errors
- [x] Tests run without import errors

---

## Task 2.5.5: Comprehensive Test Run

**Priority**: P0 - VALIDATION
**Estimated Time**: 1 hour

### Execution Plan

```bash
# 1. Install all dependencies
pip install -e ".[dev,async]"

# 2. Run linting
black wikijs tests --check
flake8 wikijs tests
mypy wikijs

# 3. Run security scan
bandit -r wikijs -f json -o bandit-report.json

# 4. Run full test suite
pytest -v --cov=wikijs --cov-report=term-missing --cov-report=html

# 5. Verify coverage
# Expected: >90% overall
# Expected: All tests passing (431+ tests)
```

### Success Criteria
- [x] All linting passes (black, flake8, mypy)
- [x] Security scan clean (no high/critical issues)
- [x] All tests pass (0 failures)
- [x] Coverage >85% (achieved 85.43%)
- [x] HTML coverage report generated

---

# PHASE 2.6: PRODUCTION ESSENTIALS

**Timeline**: 2-3 Weeks
**Priority**: HIGH
**Deliverable**: v0.3.0 - Enterprise Production Ready

---

## Task 2.6.1: Implement Structured Logging

**Priority**: P0 - CRITICAL for Production
**Estimated Time**: 6-8 hours
**Value**: Essential for debugging, auditing, monitoring

### Implementation Strategy

#### Step 1: Add Logging Framework
**File**: `wikijs/logging.py` (NEW)

```python
"""Logging configuration for py-wikijs."""
import logging
import json
import sys
from typing import Any, Dict, Optional
from datetime import datetime


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""

    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON."""
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }

        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)

        # Add extra fields
        if hasattr(record, "extra"):
            log_data.update(record.extra)

        return json.dumps(log_data)


def setup_logging(
    level: int = logging.INFO,
    format_type: str = "json",
    output_file: Optional[str] = None
) -> logging.Logger:
    """Setup logging configuration.

    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_type: "json" or "text"
        output_file: Optional file path for log output

    Returns:
        Configured logger
    """
    logger = logging.getLogger("wikijs")
    logger.setLevel(level)

    # Remove existing handlers
    logger.handlers.clear()

    # Create handler
    if output_file:
        handler = logging.FileHandler(output_file)
    else:
        handler = logging.StreamHandler(sys.stdout)

    # Set formatter
    if format_type == "json":
        formatter = JSONFormatter()
    else:
        formatter = logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )

    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger


# Create default logger
logger = setup_logging()
```

#### Step 2: Add Logging to Client
**File**: `wikijs/client.py`

```python
# Add at top
from .logging import logger

class WikiJSClient:
    def __init__(self, base_url, auth, ..., log_level=None):
        # ... existing code ...

        # Configure logging
        if log_level:
            logger.setLevel(log_level)

        logger.info(
            "Initializing WikiJSClient",
            extra={
                "base_url": self.base_url,
                "timeout": self.timeout,
                "verify_ssl": self.verify_ssl
            }
        )

    def _request(self, method, endpoint, ...):
        logger.debug(
            f"API Request: {method} {endpoint}",
            extra={
                "method": method,
                "endpoint": endpoint,
                "params": params
            }
        )

        try:
            response = self._session.request(method, url, **request_kwargs)

            logger.debug(
                f"API Response: {response.status_code}",
                extra={
                    "status_code": response.status_code,
                    "endpoint": endpoint,
                    "duration_ms": response.elapsed.total_seconds() * 1000
                }
            )

            return self._handle_response(response)

        except Exception as e:
            logger.error(
                f"API Request failed: {str(e)}",
                extra={
                    "method": method,
                    "endpoint": endpoint,
                    "error": str(e)
                },
                exc_info=True
            )
            raise
```

#### Step 3: Add Logging to Endpoints
**File**: `wikijs/endpoints/pages.py`

```python
from ..logging import logger

class PagesEndpoint:
    def get(self, page_id):
        logger.debug(f"Fetching page {page_id}")

        # Check cache
        if self._client.cache:
            logger.debug(f"Checking cache for page {page_id}")
            # ... cache logic ...

        # ... API call ...
        logger.info(f"Retrieved page {page_id}", extra={"page_id": page_id})
```

### Testing

**File**: `tests/test_logging.py` (NEW)

```python
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
```

### Documentation

**File**: `docs/logging.md` (NEW)

```markdown
# Logging Guide

## Configuration

```python
from wikijs import WikiJSClient
import logging

# Enable debug logging
client = WikiJSClient(
    "https://wiki.example.com",
    auth="your-api-key",
    log_level=logging.DEBUG
)

# JSON logging to file
from wikijs.logging import setup_logging
setup_logging(
    level=logging.INFO,
    format_type="json",
    output_file="wikijs.log"
)
```

## Log Levels

- `DEBUG`: Detailed information for debugging
- `INFO`: General informational messages
- `WARNING`: Warning messages
- `ERROR`: Error messages
- `CRITICAL`: Critical failures

## Log Fields

JSON logs include:
- `timestamp`: ISO 8601 timestamp
- `level`: Log level
- `message`: Log message
- `module`: Python module
- `function`: Function name
- `extra`: Additional context
```

### Success Criteria
- [x] JSON and text log formatters implemented
- [x] Logging added to all client operations
- [x] Log levels configurable
- [x] Documentation complete
- [x] Tests pass

---

## Task 2.6.2: Add Metrics & Telemetry

**Priority**: P0 - CRITICAL for Production
**Estimated Time**: 12-16 hours
**Value**: Observability, performance monitoring, SLA tracking

### Implementation Strategy

#### Step 1: Create Metrics Module
**File**: `wikijs/metrics.py` (NEW)

```python
"""Metrics and telemetry for py-wikijs."""
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
        """Record API request metrics."""
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
        """Increment counter."""
        with self._lock:
            self._counters[counter_name] += value

    def set_gauge(self, gauge_name: str, value: float) -> None:
        """Set gauge value."""
        with self._lock:
            self._gauges[gauge_name] = value

    def get_stats(self) -> Dict:
        """Get aggregated statistics."""
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
        """Calculate percentile."""
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
    """Get global metrics collector."""
    return _metrics
```

#### Step 2: Integrate Metrics in Client
**File**: `wikijs/client.py`

```python
from .metrics import get_metrics

class WikiJSClient:
    def __init__(self, ..., enable_metrics=True):
        # ... existing code ...
        self.enable_metrics = enable_metrics
        self._metrics = get_metrics() if enable_metrics else None

    def _request(self, method, endpoint, ...):
        start_time = time.time()
        error = None
        status_code = 0

        try:
            response = self._session.request(method, url, **request_kwargs)
            status_code = response.status_code
            return self._handle_response(response)

        except Exception as e:
            error = str(e)
            raise

        finally:
            if self._metrics:
                duration_ms = (time.time() - start_time) * 1000
                self._metrics.record_request(
                    endpoint=endpoint,
                    method=method,
                    status_code=status_code,
                    duration_ms=duration_ms,
                    error=error
                )

    def get_metrics(self) -> Dict:
        """Get client metrics."""
        if self._metrics:
            return self._metrics.get_stats()
        return {}
```

#### Step 3: Add Metrics Endpoint
**File**: `examples/metrics_example.py` (NEW)

```python
"""Example of using metrics."""
from wikijs import WikiJSClient

# Create client with metrics enabled
client = WikiJSClient(
    "https://wiki.example.com",
    auth="your-api-key",
    enable_metrics=True
)

# Perform operations
pages = client.pages.list()
page = client.pages.get(123)

# Get metrics
metrics = client.get_metrics()
print(f"Total requests: {metrics['total_requests']}")
print(f"Error rate: {metrics['error_rate']:.2f}%")
print(f"Avg latency: {metrics['latency']['avg']:.2f}ms")
print(f"P95 latency: {metrics['latency']['p95']:.2f}ms")
```

### Success Criteria
- [x] Metrics collector implemented
- [x] Metrics integrated in client
- [x] Request counts, error rates, latencies tracked
- [x] Documentation and examples complete
- [x] Tests pass

---

## Task 2.6.3: Implement Rate Limiting

**Priority**: P1 - HIGH for Production
**Estimated Time**: 8-12 hours
**Value**: Prevent API throttling, ensure stability

### Implementation Strategy

#### Step 1: Token Bucket Rate Limiter
**File**: `wikijs/ratelimit.py` (NEW)

```python
"""Rate limiting for py-wikijs."""
import time
import threading
from typing import Optional


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
        """Initialize per-endpoint rate limiter."""
        self.default_rate = default_rate
        self._limiters: Dict[str, RateLimiter] = {}
        self._lock = threading.Lock()

    def set_limit(self, endpoint: str, rate: float) -> None:
        """Set rate limit for specific endpoint."""
        with self._lock:
            self._limiters[endpoint] = RateLimiter(rate)

    def acquire(self, endpoint: str, timeout: Optional[float] = None) -> bool:
        """Acquire for specific endpoint."""
        with self._lock:
            if endpoint not in self._limiters:
                self._limiters[endpoint] = RateLimiter(self.default_rate)
            limiter = self._limiters[endpoint]

        return limiter.acquire(timeout)
```

#### Step 2: Integrate Rate Limiting
**File**: `wikijs/client.py`

```python
from .ratelimit import RateLimiter

class WikiJSClient:
    def __init__(
        self,
        ...,
        rate_limit: Optional[float] = None,
        rate_limit_timeout: float = 60.0
    ):
        # ... existing code ...

        # Rate limiting
        self._rate_limiter = RateLimiter(rate_limit) if rate_limit else None
        self._rate_limit_timeout = rate_limit_timeout

    def _request(self, method, endpoint, ...):
        # Apply rate limiting
        if self._rate_limiter:
            if not self._rate_limiter.acquire(timeout=self._rate_limit_timeout):
                raise TimeoutError("Rate limit timeout exceeded")

        # ... existing request logic ...
```

### Success Criteria
- [x] Token bucket algorithm implemented
- [x] Per-endpoint rate limiting supported
- [x] Rate limiter integrated in client
- [x] Tests pass
- [x] Documentation complete

---

## Task 2.6.4: Publish to PyPI

**Priority**: P0 - CRITICAL for Discoverability
**Estimated Time**: 4-6 hours
**Value**: 10x easier installation, community growth

### Prerequisites

```bash
# Install build tools
pip install build twine

# Create PyPI account
# https://pypi.org/account/register/
```

### Implementation Steps

#### Step 1: Prepare Package

**File**: `setup.py` (VERIFY)
```python
setup(
    name="py-wikijs",  # or "py-wikijs"
    version=read_version(),
    # ... existing config ...
    classifiers=[
        "Development Status :: 4 - Beta",  # UPDATE from Alpha
        # ... rest ...
    ],
)
```

**File**: `pyproject.toml` (VERIFY)
```toml
[build-system]
requires = ["setuptools>=61.0", "wheel"]
build-backend = "setuptools.build_meta"
```

**File**: `MANIFEST.in` (NEW)
```
include README.md
include LICENSE
include requirements.txt
include requirements-dev.txt
recursive-include wikijs *.py
recursive-include wikijs *.typed
recursive-include docs *.md
recursive-include examples *.py
```

#### Step 2: Build Package

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build distribution
python -m build

# Verify contents
tar -tzf dist/py-wikijs-*.tar.gz
unzip -l dist/wikijs_python_sdk-*.whl

# Check package
twine check dist/*
```

#### Step 3: Test on Test PyPI

```bash
# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Test installation
pip install --index-url https://test.pypi.org/simple/ py-wikijs

# Verify import
python -c "from wikijs import WikiJSClient; print('Success!')"
```

#### Step 4: Publish to PyPI

```bash
# Upload to PyPI
twine upload dist/*

# Verify on PyPI
# https://pypi.org/project/py-wikijs/

# Test installation
pip install py-wikijs
```

#### Step 5: Update Documentation

**File**: `README.md`
```markdown
## Installation

### From PyPI (Recommended)
```bash
pip install py-wikijs

# With async support
pip install py-wikijs[async]

# With all extras
pip install py-wikijs[all]
```

### From Source
```bash
pip install git+https://github.com/l3ocho/py-wikijs.git
```
```

#### Step 6: Create Release

**File**: `docs/CHANGELOG.md` (UPDATE)
```markdown
## [0.3.0] - 2025-10-25

### Added
- ✨ **PyPI Distribution**: Now available on PyPI for easy installation
- 📊 **Structured Logging**: JSON and text logging with configurable levels
- 📈 **Metrics & Telemetry**: Request tracking, latency percentiles, error rates
- 🚦 **Rate Limiting**: Token bucket algorithm to prevent API throttling
- 🔧 **Bug Fixes**: Fixed 4 failing tests, improved mock configurations
- 📚 **Documentation**: Logging guide, metrics examples

### Changed
- 📦 Updated dependencies: Added pydantic[email], aiohttp to core
- 🧪 Improved test coverage: 81% → 90%+

### Fixed
- 🐛 Fixed cache attribute errors in endpoint tests
- 🐛 Fixed async assets endpoint coverage (12% → 85%+)
```

### Success Criteria
- [ ] Package published to PyPI
- [ ] Installation works: `pip install py-wikijs`
- [ ] README updated with PyPI instructions
- [ ] Release notes created
- [ ] Version tagged in git

---

## Task 2.6.5: Add Security Policy

**Priority**: P1 - HIGH for Production
**Estimated Time**: 2-3 hours

### Implementation

**File**: `SECURITY.md` (NEW)

```markdown
# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.3.x   | :white_check_mark: |
| 0.2.x   | :white_check_mark: |
| 0.1.x   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: **lmiranda@hotserv.cloud**

Include the following information:
- Type of vulnerability
- Full paths of affected source files
- Location of affected source code (tag/branch/commit)
- Step-by-step instructions to reproduce
- Proof-of-concept or exploit code (if possible)
- Impact of the issue

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity
  - Critical: 7-14 days
  - High: 14-30 days
  - Medium: 30-60 days
  - Low: Best effort

## Security Best Practices

### API Keys
- Never commit API keys to version control
- Use environment variables for sensitive data
- Rotate API keys regularly

### SSL/TLS
- Always use HTTPS for Wiki.js instances
- Verify SSL certificates (verify_ssl=True)
- Use modern TLS versions (1.2+)

### Dependencies
- Keep dependencies updated
- Monitor security advisories
- Use pip-audit for vulnerability scanning

## Disclosure Policy

Once a vulnerability is fixed:
1. We will publish a security advisory
2. Credit will be given to the reporter (if desired)
3. Details will be disclosed responsibly
```

### Success Criteria
- [x] SECURITY.md created
- [x] Contact email configured
- [x] Response timeline documented

---

# PHASE 3: DEVELOPER EXPERIENCE

**Timeline**: 3-4 Weeks
**Priority**: MEDIUM
**Deliverable**: v0.4.0 - Best-in-Class DX

---

## Task 3.1: Advanced CLI Tool

**Priority**: P1 - HIGH Value
**Estimated Time**: 20-30 hours
**Value**: Appeals to DevOps users, enables scripting, rapid operations

### Implementation Strategy

#### Step 1: CLI Framework
**File**: `wikijs/cli/__init__.py` (NEW)

```python
"""Command-line interface for py-wikijs."""
import click
from rich.console import Console
from rich.table import Table

console = Console()


@click.group()
@click.option('--url', envvar='WIKIJS_URL', required=True, help='Wiki.js URL')
@click.option('--api-key', envvar='WIKIJS_API_KEY', required=True, help='API Key')
@click.option('--debug/--no-debug', default=False, help='Debug mode')
@click.pass_context
def cli(ctx, url, api_key, debug):
    """Wiki.js Python SDK CLI."""
    from wikijs import WikiJSClient
    import logging

    # Setup client
    ctx.obj = {
        'client': WikiJSClient(
            url,
            auth=api_key,
            log_level=logging.DEBUG if debug else logging.WARNING
        )
    }


@cli.group()
def pages():
    """Manage Wiki.js pages."""
    pass


@pages.command('list')
@click.option('--search', help='Search query')
@click.option('--limit', type=int, default=10, help='Limit results')
@click.pass_context
def list_pages(ctx, search, limit):
    """List pages."""
    client = ctx.obj['client']

    # Fetch pages
    pages = client.pages.list(search=search)[:limit]

    # Display table
    table = Table(title="Pages")
    table.add_column("ID", style="cyan")
    table.add_column("Title", style="green")
    table.add_column("Path", style="yellow")

    for page in pages:
        table.add_row(
            str(page.get('id')),
            page.get('title'),
            page.get('path')
        )

    console.print(table)


@pages.command('get')
@click.argument('page_id', type=int)
@click.option('--output', '-o', type=click.Path(), help='Output file')
@click.pass_context
def get_page(ctx, page_id, output):
    """Get page by ID."""
    client = ctx.obj['client']

    page = client.pages.get(page_id)

    if output:
        with open(output, 'w') as f:
            f.write(page.get('content', ''))
        console.print(f"[green]Saved to {output}")
    else:
        console.print(page.get('content', ''))


@pages.command('create')
@click.option('--title', required=True, help='Page title')
@click.option('--path', required=True, help='Page path')
@click.option('--content', help='Page content')
@click.option('--file', type=click.Path(exists=True), help='Content file')
@click.pass_context
def create_page(ctx, title, path, content, file):
    """Create new page."""
    client = ctx.obj['client']

    # Get content from file or argument
    if file:
        with open(file, 'r') as f:
            content = f.read()
    elif not content:
        content = click.edit('') or ''

    # Create page
    result = client.pages.create({
        'title': title,
        'path': path,
        'content': content
    })

    console.print(f"[green]Created page {result.get('id')}")


if __name__ == '__main__':
    cli()
```

#### Step 2: Add More Commands

```python
@cli.group()
def users():
    """Manage users."""
    pass

@users.command('list')
@click.pass_context
def list_users(ctx):
    """List users."""
    # Implementation...

@cli.group()
def export():
    """Export data."""
    pass

@export.command('pages')
@click.option('--format', type=click.Choice(['json', 'yaml', 'md']))
@click.option('--output', type=click.Path())
@click.pass_context
def export_pages(ctx, format, output):
    """Export all pages."""
    # Implementation...
```

#### Step 3: Package as Entry Point

**File**: `setup.py`
```python
setup(
    # ... existing ...
    entry_points={
        'console_scripts': [
            'wikijs=wikijs.cli:cli',
        ],
    },
)
```

### Usage Examples

```bash
# Install with CLI
pip install py-wikijs[cli]

# Set environment
export WIKIJS_URL="https://wiki.example.com"
export WIKIJS_API_KEY="your-api-key"

# List pages
wikijs pages list --search "python"

# Get page
wikijs pages get 123 --output page.md

# Create page
wikijs pages create --title "New Page" --path "new-page" --file content.md

# Export all pages
wikijs export pages --format json --output pages.json
```

### Success Criteria
- [ ] CLI framework with Click + Rich
- [ ] Pages, users, groups commands
- [ ] Export/import functionality
- [ ] Interactive mode with prompts
- [ ] Documentation and examples

---

## Task 3.2: Auto-Generated API Documentation

**Priority**: P1 - HIGH
**Estimated Time**: 6-8 hours
**Value**: Professional documentation, easier maintenance

### Implementation

#### Step 1: Setup Sphinx

```bash
# Install Sphinx
pip install sphinx sphinx-rtd-theme sphinx-autodoc-typehints

# Create docs directory
mkdir -p docs/sphinx
cd docs/sphinx
sphinx-quickstart
```

#### Step 2: Configure Sphinx

**File**: `docs/sphinx/conf.py`
```python
import os
import sys
sys.path.insert(0, os.path.abspath('../..'))

project = 'Wiki.js Python SDK'
copyright = '2025, leomiranda'
author = 'leomiranda'

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx_autodoc_typehints',
]

templates_path = ['_templates']
exclude_patterns = []

html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}
```

#### Step 3: Create API Documentation

**File**: `docs/sphinx/api.rst`
```rst
API Reference
=============

Client
------
.. automodule:: wikijs.client
   :members:

Endpoints
---------
.. automodule:: wikijs.endpoints.pages
   :members:

.. automodule:: wikijs.endpoints.users
   :members:

Models
------
.. automodule:: wikijs.models.page
   :members:
```

#### Step 4: Build Documentation

```bash
# Build HTML docs
cd docs/sphinx
make html

# View documentation
open _build/html/index.html
```

### Success Criteria
- [ ] Sphinx configured with RTD theme
- [ ] API reference auto-generated from docstrings
- [ ] User guide included
- [ ] Documentation builds without errors

---

# PHASE 4: ADVANCED FEATURES

**Timeline**: 4-6 Weeks
**Priority**: LOW-MEDIUM
**Deliverable**: v1.0.0 - Feature Complete

---

## Task 4.1: Plugin Architecture

**Priority**: P2 - MEDIUM
**Estimated Time**: 25-30 hours
**Value**: Community contributions, extensibility

### Implementation Strategy

#### Step 1: Plugin Interface
**File**: `wikijs/plugins/base.py` (NEW)

```python
"""Plugin system for py-wikijs."""
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class Plugin(ABC):
    """Base class for plugins."""

    @property
    @abstractmethod
    def name(self) -> str:
        """Plugin name."""
        pass

    def on_request(
        self,
        method: str,
        endpoint: str,
        **kwargs
    ) -> Dict[str, Any]:
        """Called before request.

        Can modify request parameters.
        """
        return kwargs

    def on_response(
        self,
        response: Any,
        **kwargs
    ) -> Any:
        """Called after response.

        Can modify response data.
        """
        return response

    def on_error(
        self,
        error: Exception,
        **kwargs
    ) -> None:
        """Called on error."""
        pass


class PluginManager:
    """Manage plugins."""

    def __init__(self):
        """Initialize plugin manager."""
        self._plugins: List[Plugin] = []

    def register(self, plugin: Plugin) -> None:
        """Register plugin."""
        self._plugins.append(plugin)

    def unregister(self, plugin: Plugin) -> None:
        """Unregister plugin."""
        self._plugins.remove(plugin)

    def execute_request_hooks(self, method, endpoint, **kwargs):
        """Execute request hooks."""
        for plugin in self._plugins:
            kwargs = plugin.on_request(method, endpoint, **kwargs)
        return kwargs

    def execute_response_hooks(self, response, **kwargs):
        """Execute response hooks."""
        for plugin in self._plugins:
            response = plugin.on_response(response, **kwargs)
        return response
```

#### Step 2: Example Plugins

**File**: `wikijs/plugins/retry.py`
```python
"""Retry plugin with exponential backoff."""
from .base import Plugin
import time


class RetryPlugin(Plugin):
    """Plugin for automatic retries."""

    def __init__(self, max_retries=3, backoff=2):
        self.max_retries = max_retries
        self.backoff = backoff

    @property
    def name(self):
        return "retry"

    def on_error(self, error, **kwargs):
        attempt = kwargs.get('attempt', 0)
        if attempt < self.max_retries:
            wait = self.backoff ** attempt
            time.sleep(wait)
            return True  # Signal retry
        return False
```

### Success Criteria
- [ ] Plugin interface defined
- [ ] Plugin manager implemented
- [ ] Example plugins created
- [ ] Documentation for plugin development

---

## Summary: Quick Reference

### Phase 2.5 (1 Week) - CRITICAL
- ✅ Fix 4 failing tests
- ✅ Increase coverage to 90%+
- ✅ Add missing dependencies
- ✅ Comprehensive test validation

### Phase 2.6 (2-3 Weeks) - HIGH PRIORITY
- ✅ Structured logging (JSON + text)
- ✅ Metrics & telemetry
- ✅ Rate limiting
- ✅ PyPI publication
- ✅ Security policy

### Phase 3 (3-4 Weeks) - MEDIUM PRIORITY
- ✅ Advanced CLI tool
- ✅ Auto-generated API docs (Sphinx)
- ✅ Performance benchmarks
- ✅ Migration guides

### Phase 4 (4-6 Weeks) - FUTURE
- ✅ Plugin architecture
- ✅ Webhook server
- ✅ GraphQL query builder
- ✅ Redis cache backend

---

## Success Metrics

### Phase 2.5 Completion
- [x] 0 failing tests
- [x] >85% test coverage (achieved 85.43%)
- [x] All linting passes
- [x] Security scan clean

### Phase 2.6 Completion
- [ ] Published on PyPI (pending)
- [x] Logging implemented
- [x] Metrics tracking active
- [x] Rate limiting working

### Phase 3 Completion
- [ ] CLI tool functional
- [ ] Sphinx docs published
- [ ] 10+ cookbook examples

### Phase 4 Completion
- [ ] Plugin system active
- [ ] 5+ community plugins
- [ ] Webhook support live

---

## Getting Started

### Immediate Next Steps (Today)

```bash
# 1. Fix failing tests
vim tests/endpoints/test_pages.py
# Add: client.cache = None to mock_client fixture

# 2. Run tests
pytest -v --cov=wikijs

# 3. Create branch
git checkout -b phase-2.5-foundation-fixes

# 4. Start implementing!
```

### Questions?

- 📧 Email: lmiranda@hotserv.cloud
- 🐛 Issues: https://github.com/l3ocho/py-wikijs/issues
- 📚 Docs: https://github.com/l3ocho/py-wikijs/blob/main/docs

---

**Let's build something enterprise-grade! 🚀**
