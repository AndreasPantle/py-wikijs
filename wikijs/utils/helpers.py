"""Helper utilities for wikijs-python-sdk."""

import re
from typing import Any, Dict, Optional
from urllib.parse import urljoin, urlparse

from ..exceptions import APIError, ValidationError


def normalize_url(base_url: str) -> str:
    """Normalize a base URL for API usage.
    
    Args:
        base_url: Base URL to normalize
        
    Returns:
        Normalized URL without trailing slash
        
    Raises:
        ValidationError: If URL is invalid
    """
    if not base_url:
        raise ValidationError("Base URL cannot be empty")
    
    # Add https:// if no scheme provided
    if not base_url.startswith(("http://", "https://")):
        base_url = f"https://{base_url}"
    
    # Validate URL format
    if not validate_url(base_url):
        raise ValidationError(f"Invalid URL format: {base_url}")
    
    # Remove trailing slash
    return base_url.rstrip("/")


def validate_url(url: str) -> bool:
    """Validate URL format.
    
    Args:
        url: URL to validate
        
    Returns:
        True if URL is valid
    """
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except Exception:
        return False


def sanitize_path(path: str) -> str:
    """Sanitize a wiki page path.
    
    Args:
        path: Path to sanitize
        
    Returns:
        Sanitized path
        
    Raises:
        ValidationError: If path is invalid
    """
    if not path:
        raise ValidationError("Path cannot be empty")
    
    # Remove leading/trailing slashes and whitespace
    path = path.strip().strip("/")
    
    # Replace spaces with hyphens
    path = re.sub(r"\s+", "-", path)
    
    # Remove invalid characters, keep only alphanumeric, hyphens, underscores, slashes
    path = re.sub(r"[^a-zA-Z0-9\-_/]", "", path)
    
    # Remove multiple consecutive hyphens or slashes
    path = re.sub(r"[-/]+", lambda m: m.group(0)[0], path)
    
    if not path:
        raise ValidationError("Path contains no valid characters")
    
    return path


def build_api_url(base_url: str, endpoint: str) -> str:
    """Build full API URL from base URL and endpoint.
    
    Args:
        base_url: Base URL (already normalized)
        endpoint: API endpoint path
        
    Returns:
        Full API URL
    """
    # Ensure endpoint starts with /
    if not endpoint.startswith("/"):
        endpoint = f"/{endpoint}"
    
    # Wiki.js API is typically at /graphql, but we'll use REST-style for now
    api_base = f"{base_url}/api"
    
    return urljoin(api_base, endpoint.lstrip("/"))


def parse_wiki_response(response_data: Dict[str, Any]) -> Dict[str, Any]:
    """Parse Wiki.js API response data.
    
    Args:
        response_data: Raw response data from API
        
    Returns:
        Parsed response data
        
    Raises:
        APIError: If response indicates an error
    """
    if not isinstance(response_data, dict):
        return response_data
    
    # Check for error indicators
    if "error" in response_data:
        error_info = response_data["error"]
        if isinstance(error_info, dict):
            message = error_info.get("message", "Unknown API error")
            code = error_info.get("code")
        else:
            message = str(error_info)
            code = None
        
        raise APIError(f"API Error: {message}", details={"code": code})
    
    # Handle GraphQL-style errors
    if "errors" in response_data:
        errors = response_data["errors"]
        if errors:
            first_error = errors[0] if isinstance(errors, list) else errors
            message = first_error.get("message", "GraphQL error") if isinstance(first_error, dict) else str(first_error)
            raise APIError(f"GraphQL Error: {message}", details={"errors": errors})
    
    return response_data


def extract_error_message(response: Any) -> str:
    """Extract error message from response.
    
    Args:  
        response: Response object or data
        
    Returns:
        Error message string
    """
    if hasattr(response, "json"):
        try:
            data = response.json()
            if isinstance(data, dict):
                # Try common error message fields
                for field in ["message", "error", "detail", "msg"]:
                    if field in data:
                        return str(data[field])
        except Exception:
            pass
    
    if hasattr(response, "text"):
        return response.text[:200] + "..." if len(response.text) > 200 else response.text
    
    return str(response)


def chunk_list(items: list, chunk_size: int) -> list:
    """Split list into chunks of specified size.
    
    Args:
        items: List to chunk
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    if chunk_size <= 0:
        raise ValueError("Chunk size must be positive")
    
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]


def safe_get(data: Dict[str, Any], key: str, default: Any = None) -> Any:
    """Safely get value from dictionary with dot notation support.
    
    Args:
        data: Dictionary to get value from
        key: Key (supports dot notation like "user.name")
        default: Default value if key not found
        
    Returns:
        Value or default
    """
    if "." not in key:
        return data.get(key, default)
    
    keys = key.split(".")
    current = data
    
    for k in keys:
        if isinstance(current, dict) and k in current:
            current = current[k]
        else:
            return default
    
    return current