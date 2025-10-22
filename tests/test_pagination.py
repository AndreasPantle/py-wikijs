"""Tests for auto-pagination iterators."""

from unittest.mock import AsyncMock, Mock

import pytest

from wikijs.aio.endpoints import AsyncPagesEndpoint, AsyncUsersEndpoint
from wikijs.endpoints import PagesEndpoint, UsersEndpoint
from wikijs.models import Page, User


class TestPagesIterator:
    """Test Pages iterator."""

    @pytest.fixture
    def client(self):
        """Create mock client."""
        return Mock(base_url="https://wiki.example.com")

    @pytest.fixture
    def endpoint(self, client):
        """Create PagesEndpoint."""
        return PagesEndpoint(client)

    def test_iter_all_single_batch(self, endpoint):
        """Test iteration with single batch."""
        # Mock list to return 3 pages (less than batch size)
        pages_data = [
            Page(id=i, title=f"Page {i}", path=f"/page{i}", content="test",
                 created_at="2024-01-01T00:00:00Z", updated_at="2024-01-01T00:00:00Z")
            for i in range(1, 4)
        ]
        endpoint.list = Mock(return_value=pages_data)

        # Iterate
        result = list(endpoint.iter_all(batch_size=50))

        # Should fetch once and return all 3
        assert len(result) == 3
        assert endpoint.list.call_count == 1

    def test_iter_all_multiple_batches(self, endpoint):
        """Test iteration with multiple batches."""
        # Mock list to return different batches
        batch1 = [
            Page(id=i, title=f"Page {i}", path=f"/page{i}", content="test",
                 created_at="2024-01-01T00:00:00Z", updated_at="2024-01-01T00:00:00Z")
            for i in range(1, 3)
        ]
        batch2 = [
            Page(id=3, title="Page 3", path="/page3", content="test",
                 created_at="2024-01-01T00:00:00Z", updated_at="2024-01-01T00:00:00Z")
        ]
        endpoint.list = Mock(side_effect=[batch1, batch2])

        # Iterate with batch_size=2
        result = list(endpoint.iter_all(batch_size=2))

        # Should fetch twice and return all 3
        assert len(result) == 3
        assert endpoint.list.call_count == 2

    def test_iter_all_empty(self, endpoint):
        """Test iteration with no results."""
        endpoint.list = Mock(return_value=[])

        result = list(endpoint.iter_all())

        assert len(result) == 0
        assert endpoint.list.call_count == 1


class TestUsersIterator:
    """Test Users iterator."""

    @pytest.fixture
    def client(self):
        """Create mock client."""
        return Mock(base_url="https://wiki.example.com")

    @pytest.fixture
    def endpoint(self, client):
        """Create UsersEndpoint."""
        return UsersEndpoint(client)

    def test_iter_all_pagination(self, endpoint):
        """Test pagination with users."""
        # Create 5 users, batch size 2
        all_users = [
            User(id=i, name=f"User {i}", email=f"user{i}@example.com",
                 created_at="2024-01-01T00:00:00Z", updated_at="2024-01-01T00:00:00Z")
            for i in range(1, 6)
        ]
        
        # Mock to return batches
        endpoint.list = Mock(side_effect=[
            all_users[0:2],  # First batch
            all_users[2:4],  # Second batch
            all_users[4:5],  # Third batch (last, < batch_size)
        ])

        result = list(endpoint.iter_all(batch_size=2))

        assert len(result) == 5
        assert endpoint.list.call_count == 3


class TestAsyncPagesIterator:
    """Test async Pages iterator."""

    @pytest.fixture
    def client(self):
        """Create mock async client."""
        return Mock(base_url="https://wiki.example.com")

    @pytest.fixture
    def endpoint(self, client):
        """Create AsyncPagesEndpoint."""
        return AsyncPagesEndpoint(client)

    @pytest.mark.asyncio
    async def test_iter_all_async(self, endpoint):
        """Test async iteration."""
        pages_data = [
            Page(id=i, title=f"Page {i}", path=f"/page{i}", content="test",
                 created_at="2024-01-01T00:00:00Z", updated_at="2024-01-01T00:00:00Z")
            for i in range(1, 4)
        ]
        endpoint.list = AsyncMock(return_value=pages_data)

        result = []
        async for page in endpoint.iter_all():
            result.append(page)

        assert len(result) == 3
        assert endpoint.list.call_count == 1

    @pytest.mark.asyncio
    async def test_iter_all_multiple_batches_async(self, endpoint):
        """Test async iteration with multiple batches."""
        batch1 = [
            Page(id=i, title=f"Page {i}", path=f"/page{i}", content="test",
                 created_at="2024-01-01T00:00:00Z", updated_at="2024-01-01T00:00:00Z")
            for i in range(1, 3)
        ]
        batch2 = [
            Page(id=3, title="Page 3", path="/page3", content="test",
                 created_at="2024-01-01T00:00:00Z", updated_at="2024-01-01T00:00:00Z")
        ]
        endpoint.list = AsyncMock(side_effect=[batch1, batch2])

        result = []
        async for page in endpoint.iter_all(batch_size=2):
            result.append(page)

        assert len(result) == 3
        assert endpoint.list.call_count == 2


class TestAsyncUsersIterator:
    """Test async Users iterator."""

    @pytest.fixture
    def client(self):
        """Create mock async client."""
        return Mock(base_url="https://wiki.example.com")

    @pytest.fixture
    def endpoint(self, client):
        """Create AsyncUsersEndpoint."""
        return AsyncUsersEndpoint(client)

    @pytest.mark.asyncio
    async def test_iter_all_async_pagination(self, endpoint):
        """Test async pagination."""
        all_users = [
            User(id=i, name=f"User {i}", email=f"user{i}@example.com",
                 created_at="2024-01-01T00:00:00Z", updated_at="2024-01-01T00:00:00Z")
            for i in range(1, 4)
        ]
        
        endpoint.list = AsyncMock(side_effect=[
            all_users[0:2],
            all_users[2:3],
        ])

        result = []
        async for user in endpoint.iter_all(batch_size=2):
            result.append(user)

        assert len(result) == 3
        assert endpoint.list.call_count == 2
