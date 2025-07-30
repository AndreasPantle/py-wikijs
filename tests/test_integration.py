"""Integration tests for the full WikiJS client with Pages API."""

import pytest
from unittest.mock import Mock, patch

from wikijs import WikiJSClient
from wikijs.endpoints.pages import PagesEndpoint
from wikijs.models.page import Page, PageCreate


class TestWikiJSClientIntegration:
    """Integration tests for WikiJS client with Pages API."""
    
    def test_client_has_pages_endpoint(self):
        """Test that client has pages endpoint initialized."""
        with patch('wikijs.client.requests.Session'):
            client = WikiJSClient("https://test.wiki", auth="test-key")
            
            assert hasattr(client, 'pages')
            assert isinstance(client.pages, PagesEndpoint)
            assert client.pages._client is client
    
    @patch('wikijs.client.requests.Session')
    def test_client_pages_integration(self, mock_session_class):
        """Test that pages endpoint works through client."""
        # Mock the session and response
        mock_session = Mock()
        mock_session_class.return_value = mock_session
        
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {
            "data": {
                "pages": [{
                    "id": 1,
                    "title": "Test Page",
                    "path": "test",
                    "content": "Content",
                    "isPublished": True,
                    "isPrivate": False,
                    "tags": [],
                    "locale": "en",
                    "createdAt": "2023-01-01T00:00:00Z",
                    "updatedAt": "2023-01-01T00:00:00Z"
                }]
            }
        }
        mock_session.request.return_value = mock_response
        
        # Create client
        client = WikiJSClient("https://test.wiki", auth="test-key")
        
        # Call pages.list() through client
        pages = client.pages.list()
        
        # Verify it works
        assert len(pages) == 1
        assert isinstance(pages[0], Page)
        assert pages[0].title == "Test Page"
        
        # Verify the request was made
        mock_session.request.assert_called_once()
        call_args = mock_session.request.call_args
        assert call_args[0][0] == "POST"  # GraphQL uses POST
        assert "/graphql" in call_args[0][1]