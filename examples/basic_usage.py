#!/usr/bin/env python3
"""
Basic usage examples for the Wiki.js Python SDK.

This script demonstrates fundamental operations like connecting,
listing pages, and basic CRUD operations.
"""

import os
from wikijs import WikiJSClient
from wikijs.models import PageCreate, PageUpdate
from wikijs.exceptions import APIError, AuthenticationError

def main():
    """Run basic usage examples."""
    
    # Get configuration from environment variables
    base_url = os.getenv("WIKIJS_URL", "https://wiki.example.com")
    api_key = os.getenv("WIKIJS_API_KEY", "your-api-key-here")
    
    print("🚀 Wiki.js Python SDK - Basic Usage Examples")
    print("=" * 50)
    
    # Initialize the client
    print(f"📡 Connecting to {base_url}...")
    
    try:
        with WikiJSClient(base_url=base_url, auth=api_key) as client:
            
            # Test connection
            print("🔍 Testing connection...")
            if client.test_connection():
                print("✅ Connected successfully!")
            else:
                print("❌ Connection failed!")
                return
            
            # Example 1: List all pages
            print("\n📚 Example 1: Listing Pages")
            print("-" * 30)
            
            pages = client.pages.list(limit=5)
            print(f"Found {len(pages)} pages (showing first 5):")
            
            for page in pages:
                print(f"  • {page.title} (ID: {page.id}, Path: /{page.path})")
            
            # Example 2: Search for pages
            print("\n🔍 Example 2: Searching Pages")
            print("-" * 30)
            
            search_results = client.pages.search("guide", limit=3)
            print(f"Found {len(search_results)} pages matching 'guide':")
            
            for page in search_results:
                print(f"  • {page.title}")
                print(f"    Words: {page.word_count}, Reading time: {page.reading_time}min")
            
            # Example 3: Get a specific page
            if pages:
                print(f"\n📄 Example 3: Getting Page Details")
                print("-" * 30)
                
                first_page = pages[0]
                page_details = client.pages.get(first_page.id)
                
                print(f"Title: {page_details.title}")
                print(f"Path: /{page_details.path}")
                print(f"Published: {page_details.is_published}")
                print(f"Tags: {', '.join(page_details.tags) if page_details.tags else 'None'}")
                print(f"Content preview: {page_details.content[:100]}...")
                
                # Show headings if available
                headings = page_details.extract_headings()
                if headings:
                    print(f"Headings: {', '.join(headings[:3])}")
            
            # Example 4: Create a new page
            print(f"\n✏️ Example 4: Creating a New Page")
            print("-" * 30)
            
            new_page_data = PageCreate(
                title="SDK Example Page",
                path="sdk-example-page",
                content="""# SDK Example Page

This page was created using the Wiki.js Python SDK!

## Features Demonstrated

- Page creation via API
- Markdown content support
- Tag assignment
- Metadata handling

## Next Steps

Try updating this page using the SDK's update functionality.
""",
                description="A demonstration page created by the Python SDK",
                tags=["sdk", "example", "python", "demo"],
                is_published=True,
                editor="markdown"
            )
            
            try:
                created_page = client.pages.create(new_page_data)
                print(f"✅ Created page: {created_page.title} (ID: {created_page.id})")
                
                # Example 5: Update the created page
                print(f"\n🔄 Example 5: Updating the Page")
                print("-" * 30)
                
                update_data = PageUpdate(
                    content=created_page.content + "\n\n## Update Log\n\n- Page updated via SDK!",
                    tags=created_page.tags + ["updated"]
                )
                
                updated_page = client.pages.update(created_page.id, update_data)
                print(f"✅ Updated page: {updated_page.title}")
                print(f"   New tag count: {len(updated_page.tags)}")
                
                # Example 6: Get page by path
                print(f"\n🔍 Example 6: Getting Page by Path")
                print("-" * 30)
                
                page_by_path = client.pages.get_by_path("sdk-example-page")
                print(f"Retrieved page: {page_by_path.title}")
                print(f"Same page? {page_by_path.id == created_page.id}")
                
                # Cleanup: Delete the created page
                print(f"\n🗑️ Cleaning up: Deleting the example page")
                print("-" * 30)
                
                if client.pages.delete(created_page.id):
                    print("✅ Example page deleted successfully")
                else:
                    print("❌ Failed to delete example page")
                
            except APIError as e:
                print(f"❌ Failed to create page: {e}")
            
            # Example 7: Working with tags
            print(f"\n🏷️ Example 7: Working with Tags")
            print("-" * 30)
            
            # Find pages with specific tags
            tagged_pages = client.pages.get_by_tags(["tutorial"], limit=3)
            print(f"Found {len(tagged_pages)} pages with 'tutorial' tag:")
            
            for page in tagged_pages:
                print(f"  • {page.title}")
                print(f"    All tags: {', '.join(page.tags)}")
            
            print(f"\n✨ All examples completed successfully!")
            
    except AuthenticationError:
        print("❌ Authentication failed!")
        print("💡 Please check your API key and permissions")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")


if __name__ == "__main__":
    print("💡 Before running this example:")
    print("   export WIKIJS_URL='https://your-wiki.example.com'")
    print("   export WIKIJS_API_KEY='your-api-key'")
    print()
    
    main()