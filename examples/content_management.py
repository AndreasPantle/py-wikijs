#!/usr/bin/env python3
"""
Content management examples for the Wiki.js Python SDK.

This script demonstrates advanced content management operations
like bulk operations, content migration, and template usage.
"""

import os
import time
from datetime import datetime
from wikijs import WikiJSClient
from wikijs.models import PageCreate, PageUpdate
from wikijs.exceptions import APIError

def create_page_template(template_type, **kwargs):
    """Create page content from templates."""
    
    templates = {
        "meeting_notes": """# {title}

**Date:** {date}
**Attendees:** {attendees}
**Duration:** {duration}

## Agenda
{agenda}

## Discussion Points
{discussion}

## Decisions Made
{decisions}

## Action Items
{action_items}

## Next Meeting
**Date:** {next_meeting_date}
**Topics:** {next_meeting_topics}
""",
        
        "project_doc": """# {project_name}

## Project Overview
{overview}

## Objectives
{objectives}

## Scope
### In Scope
{in_scope}

### Out of Scope  
{out_of_scope}

## Timeline
{timeline}

## Resources
### Team Members
{team_members}

### Budget
{budget}

## Risks and Mitigation
{risks}

## Success Criteria
{success_criteria}

## Status Updates
*Last updated: {last_updated}*

{status}
""",
        
        "api_doc": """# {api_name} API

## Overview
{overview}

## Base URL
```
{base_url}
```

## Authentication
{authentication}

## Endpoints

### {endpoint_name}
```http
{http_method} {endpoint_path}
```

**Description:** {endpoint_description}

**Parameters:**
{parameters}

**Example Request:**
```json
{example_request}
```

**Example Response:**
```json
{example_response}
```

## Error Codes
{error_codes}
""",
        
        "troubleshooting": """# {title} - Troubleshooting Guide

## Common Issues

### Issue: {issue_1_title}
**Symptoms:** {issue_1_symptoms}
**Cause:** {issue_1_cause}
**Solution:** {issue_1_solution}

### Issue: {issue_2_title}
**Symptoms:** {issue_2_symptoms}
**Cause:** {issue_2_cause}
**Solution:** {issue_2_solution}

## FAQ
{faq}

## Getting Help
{help_info}

## Related Documentation
{related_docs}
"""
    }
    
    template = templates.get(template_type)
    if not template:
        raise ValueError(f"Unknown template type: {template_type}")
    
    return template.format(**kwargs)


def bulk_create_pages(client, pages_data):
    """Create multiple pages with error handling and progress tracking."""
    
    created_pages = []
    failed_pages = []
    
    print(f"📝 Creating {len(pages_data)} pages...")
    
    for i, page_data in enumerate(pages_data, 1):
        try:
            print(f"  [{i}/{len(pages_data)}] Creating: {page_data.title}")
            
            created_page = client.pages.create(page_data)
            created_pages.append(created_page)
            
            # Be nice to the server
            time.sleep(0.2)
            
        except APIError as e:
            print(f"    ❌ Failed: {e}")
            failed_pages.append((page_data.title, str(e)))
    
    print(f"✅ Successfully created {len(created_pages)} pages")
    if failed_pages:
        print(f"❌ Failed to create {len(failed_pages)} pages:")
        for title, error in failed_pages:
            print(f"    • {title}: {error}")
    
    return created_pages, failed_pages


def content_migration_example(client):
    """Demonstrate content migration and format conversion."""
    
    print("🔄 Content Migration Example")
    print("-" * 40)
    
    # Find pages that need migration (example: old format markers)
    pages_to_migrate = client.pages.search("OLD_FORMAT", limit=5)
    
    if not pages_to_migrate:
        print("No pages found that need migration")
        return
    
    print(f"Found {len(pages_to_migrate)} pages to migrate")
    
    migration_count = 0
    
    for page in pages_to_migrate:
        try:
            print(f"  Migrating: {page.title}")
            
            # Example migration: Convert old-style headers
            new_content = page.content
            
            # Convert old format markers
            new_content = new_content.replace("OLD_FORMAT", "")
            new_content = new_content.replace("==Header==", "## Header")
            new_content = new_content.replace("===Subheader===", "### Subheader")
            
            # Add migration notice
            migration_notice = f"\n\n---\n*Migrated on {datetime.now().strftime('%Y-%m-%d')}*\n"
            new_content += migration_notice
            
            # Update the page
            update_data = PageUpdate(
                content=new_content,
                tags=page.tags + ["migrated"] if page.tags else ["migrated"]
            )
            
            client.pages.update(page.id, update_data)
            migration_count += 1
            
        except APIError as e:
            print(f"    ❌ Migration failed: {e}")
    
    print(f"✅ Successfully migrated {migration_count} pages")


def content_audit_example(client):
    """Perform a content audit to analyze wiki structure."""
    
    print("📊 Content Audit Example")  
    print("-" * 40)
    
    # Get all pages for analysis
    all_pages = client.pages.list()
    
    print(f"📚 Total pages: {len(all_pages)}")
    
    # Analyze by status
    published = [p for p in all_pages if p.is_published]
    private = [p for p in all_pages if p.is_private]
    
    print(f"📖 Published: {len(published)}")
    print(f"🔒 Private: {len(private)}")
    
    # Analyze by tags
    all_tags = set()
    for page in all_pages:
        if page.tags:
            all_tags.update(page.tags)
    
    print(f"🏷️ Unique tags: {len(all_tags)}")
    
    # Find most common tags
    tag_counts = {}
    for page in all_pages:
        if page.tags:
            for tag in page.tags:
                tag_counts[tag] = tag_counts.get(tag, 0) + 1
    
    if tag_counts:
        top_tags = sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:5]
        print("🔥 Most common tags:")
        for tag, count in top_tags:
            print(f"    • {tag}: {count} pages")
    
    # Analyze content length
    word_counts = [p.word_count for p in all_pages]
    if word_counts:
        avg_words = sum(word_counts) / len(word_counts)
        max_words = max(word_counts)
        min_words = min(word_counts)
        
        print(f"📝 Content analysis:")
        print(f"    • Average words: {avg_words:.0f}")
        print(f"    • Longest page: {max_words} words")
        print(f"    • Shortest page: {min_words} words")
    
    # Find pages without tags
    untagged = [p for p in all_pages if not p.tags]
    if untagged:
        print(f"⚠️ Pages without tags: {len(untagged)}")
        print("    Consider adding tags to improve organization")
    
    # Find very short pages (potential stubs)
    stubs = [p for p in all_pages if p.word_count < 50]
    if stubs:
        print(f"📝 Potential stubs (< 50 words): {len(stubs)}")
        for stub in stubs[:3]:
            print(f"    • {stub.title} ({stub.word_count} words)")


def main():
    """Run content management examples."""
    
    base_url = os.getenv("WIKIJS_URL", "https://wiki.example.com")
    api_key = os.getenv("WIKIJS_API_KEY", "your-api-key-here")
    
    print("📚 Wiki.js Python SDK - Content Management Examples")
    print("=" * 60)
    
    try:
        with WikiJSClient(base_url=base_url, auth=api_key) as client:
            
            # Test connection
            if not client.test_connection():
                print("❌ Connection failed!")
                return
            
            print("✅ Connected successfully!")
            
            # Example 1: Template-based page creation
            print("\n📝 Example 1: Template-based Page Creation")
            print("-" * 50)
            
            # Create meeting notes from template
            meeting_content = create_page_template(
                "meeting_notes",
                title="Weekly Team Sync - Dec 15, 2023",
                date="December 15, 2023",
                attendees="Alice, Bob, Charlie, Diana",
                duration="1 hour",
                agenda="• Project updates\n• Q1 planning\n• Process improvements",
                discussion="• Discussed current sprint progress\n• Reviewed Q1 roadmap priorities",
                decisions="• Approved new deployment process\n• Selected project management tool",
                action_items="• Alice: Update documentation by Dec 20\n• Bob: Set up new CI pipeline",
                next_meeting_date="December 22, 2023",
                next_meeting_topics="Holiday schedule, Q1 kickoff planning"
            )
            
            meeting_page = PageCreate(
                title="Weekly Team Sync - Dec 15, 2023",
                path="meetings/2023-12-15-team-sync",
                content=meeting_content,
                tags=["meeting", "team", "weekly"],
                description="Weekly team synchronization meeting notes"
            )
            
            # Create project documentation from template
            project_content = create_page_template(
                "project_doc",
                project_name="Wiki.js Python SDK",
                overview="A comprehensive Python SDK for interacting with Wiki.js API",
                objectives="• Provide easy-to-use Python interface\n• Support all major Wiki.js features\n• Maintain high code quality",
                in_scope="Pages API, authentication, error handling, documentation",
                out_of_scope="Advanced admin features, custom plugins",
                timeline="• Phase 1: MVP (2 weeks)\n• Phase 2: Advanced features (4 weeks)",
                team_members="• Lead Developer: Alice\n• Contributors: Community",
                budget="Open source project - volunteer contributions",
                risks="• API changes in Wiki.js\n• Community adoption",
                success_criteria="• >85% test coverage\n• Complete documentation\n• Community feedback",
                last_updated=datetime.now().strftime('%Y-%m-%d'),
                status="✅ Phase 1 completed\n🔄 Phase 2 in progress"
            )
            
            project_page = PageCreate(
                title="Wiki.js Python SDK - Project Documentation",
                path="projects/wikijs-python-sdk",
                content=project_content,
                tags=["project", "sdk", "python", "documentation"],
                description="Project documentation for the Wiki.js Python SDK"
            )
            
            # Bulk create pages
            template_pages = [meeting_page, project_page]
            created_pages, failed_pages = bulk_create_pages(client, template_pages)
            
            # Example 2: Content audit
            print("\n📊 Example 2: Content Audit")
            print("-" * 50)
            content_audit_example(client)
            
            # Example 3: Batch operations
            print("\n🔄 Example 3: Batch Tag Updates")
            print("-" * 50)
            
            # Find pages without descriptions
            pages_without_desc = client.pages.list()[:5]  # Sample for demo
            pages_to_update = [p for p in pages_without_desc if not p.description]
            
            if pages_to_update:
                print(f"Found {len(pages_to_update)} pages without descriptions")
                
                update_count = 0
                for page in pages_to_update:
                    try:
                        # Generate a basic description
                        description = f"Wiki page about {page.title.lower()}"
                        
                        update_data = PageUpdate(
                            description=description,
                            tags=page.tags + ["auto-description"] if page.tags else ["auto-description"]
                        )
                        
                        client.pages.update(page.id, update_data)
                        update_count += 1
                        print(f"  ✅ Updated: {page.title}")
                        
                    except APIError as e:
                        print(f"  ❌ Failed to update {page.title}: {e}")
                
                print(f"✅ Updated {update_count} pages with descriptions")
            else:
                print("All pages already have descriptions!")
            
            # Cleanup created pages
            print("\n🧹 Cleaning up example pages...")
            for page in created_pages:
                try:
                    client.pages.delete(page.id)
                    print(f"  🗑️ Deleted: {page.title}")
                except APIError as e:
                    print(f"  ❌ Failed to delete {page.title}: {e}")
            
            print("\n✨ Content management examples completed!")
            
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    print("💡 Before running this example:")
    print("   export WIKIJS_URL='https://your-wiki.example.com'")
    print("   export WIKIJS_API_KEY='your-api-key'")
    print()
    
    main()