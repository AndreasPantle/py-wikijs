# Wiki.js Compatibility Guide

**Last Updated**: October 2025
**SDK Version**: v0.1.0+

---

## 📋 Overview

This document provides detailed information about Wiki.js version compatibility for the py-wikijs Python SDK.

---

## ✅ Supported Versions

This SDK is compatible with **Wiki.js 2.x** (version 2.2 and higher).

### Tested Versions

| Wiki.js Version | Status | Notes |
|-----------------|--------|-------|
| **2.5.308** | ✅ Fully Tested | Current stable release |
| **2.5.x series** | ✅ Supported | All 2.5.x versions |
| **2.4.x series** | ✅ Supported | Limited testing |
| **2.3.x series** | ✅ Supported | Limited testing |
| **2.2.x series** | ✅ Supported | API baseline version |
| **2.0 - 2.1** | ⚠️ Partial | Missing API features |
| **1.x series** | ❌ Not Supported | Legacy version |
| **3.x (alpha)** | ❌ Not Supported | Different API schema |

### Version Requirements

**Minimum Requirements:**
- **Wiki.js**: 2.2 or higher
- **Python**: 3.8 or higher
- **API Access**: API key authentication enabled

**Recommended:**
- **Wiki.js**: 2.5.x (latest stable)
- **Python**: 3.10 or higher
- **Permissions**: Full admin API key for complete functionality

---

## 🔍 API Version Details

### Wiki.js 2.x API Schema

This SDK uses the **Wiki.js 2.x GraphQL API schema**, which features nested query structure:

```graphql
# Pages API (2.x)
query {
    pages {
        list(limit: 10) {
            id
            title
            path
        }
    }
}

# Users API (2.x)
query {
    users {
        list {
            id
            name
            email
        }
    }
}

# Groups API (2.x)
query {
    groups {
        list {
            id
            name
            permissions
        }
    }
}

# Assets API (2.x)
query {
    assets {
        list {
            id
            filename
            fileSize
        }
    }
}
```

### Key API Features by Version

| Feature | Version Added | SDK Support |
|---------|---------------|-------------|
| **GraphQL API** | 2.0 | ✅ |
| **API Key Authentication** | 2.2 | ✅ |
| **Pages API** | 2.2 | ✅ Full CRUD |
| **Users API** | 2.2 | ✅ Full CRUD |
| **Groups API** | 2.2 | ✅ Full CRUD |
| **Assets API** | 2.2 | ✅ Full management |
| **Page Rules** | 2.3 | ✅ Supported |
| **Batch Operations** | N/A | ✅ SDK feature |
| **Auto-Pagination** | N/A | ✅ SDK feature |

---

## ⚠️ Not Supported: Wiki.js 3.x

### Why 3.x Is Not Supported

Wiki.js 3.x (currently in alpha) introduces **breaking API changes**:

1. **Flattened GraphQL Schema**: Queries moved to root level
2. **Different Naming Convention**: `users.list` → `usersList`
3. **Modified Response Format**: Different data structures
4. **New Authentication Methods**: Updated auth flow

### Example 3.x API Difference

```graphql
# Wiki.js 2.x (Supported)
query {
    pages {
        list { id title }
    }
}

# Wiki.js 3.x (Not Supported)
query {
    pagesList { id title }
}
```

### When Will 3.x Be Supported?

Support for Wiki.js 3.x will be considered when:
- ✅ 3.x reaches stable/beta status (no ETA yet)
- ✅ API schema is finalized
- ✅ Community adoption begins

**Planned Approach**: Release as separate major version (v2.0.0 or v3.0.0) with dual support strategy.

---

## 🔧 Version Detection

### Automatic Compatibility Check

The SDK includes automatic version detection in the `test_connection()` method:

```python
from wikijs import WikiJSClient

client = WikiJSClient('https://wiki.example.com', auth='your-api-key')

try:
    if client.test_connection():
        print("✅ Compatible Wiki.js version detected")
except Exception as e:
    print(f"❌ Compatibility issue: {e}")
```

### Manual Version Check

To manually verify your Wiki.js version:

```python
from wikijs import WikiJSClient

client = WikiJSClient('https://wiki.example.com', auth='your-api-key')

# Test with a simple query
try:
    pages = client.pages.list(limit=1)
    print(f"✅ API compatible - found {len(pages)} page(s)")
except Exception as e:
    print(f"❌ API incompatible: {e}")
```

### GraphQL Introspection

You can also check the API schema directly:

```python
client = WikiJSClient('https://wiki.example.com', auth='your-api-key')

# Query for API schema information
query = """
query {
    __schema {
        queryType {
            name
        }
    }
}
"""

try:
    response = client._request("POST", "/graphql", json_data={"query": query})
    print(f"API Schema: {response}")
except Exception as e:
    print(f"Schema check failed: {e}")
```

---

## 🚀 Feature Compatibility Matrix

### Core Features

| Feature | Wiki.js 2.2 | Wiki.js 2.3 | Wiki.js 2.4 | Wiki.js 2.5 |
|---------|-------------|-------------|-------------|-------------|
| Pages CRUD | ✅ | ✅ | ✅ | ✅ |
| Users CRUD | ✅ | ✅ | ✅ | ✅ |
| Groups CRUD | ✅ | ✅ | ✅ | ✅ |
| Assets Management | ✅ | ✅ | ✅ | ✅ |
| Page Rules | ⚠️ Basic | ✅ | ✅ | ✅ |
| Batch Operations | ✅ | ✅ | ✅ | ✅ |
| Async Support | ✅ | ✅ | ✅ | ✅ |
| Caching | ✅ | ✅ | ✅ | ✅ |

### SDK Features (Version Independent)

These features work across all supported Wiki.js versions:

- ✅ **Synchronous Client**: Full support
- ✅ **Async Client**: Full support with aiohttp
- ✅ **Type Safety**: Pydantic models with validation
- ✅ **Error Handling**: Comprehensive exception hierarchy
- ✅ **Retry Logic**: Exponential backoff on failures
- ✅ **Connection Pooling**: Efficient HTTP connections
- ✅ **Batch Operations**: SDK-level batch processing
- ✅ **Auto-Pagination**: Seamless iteration over large datasets
- ✅ **Caching**: LRU cache with TTL support

---

## 🐛 Known Compatibility Issues

### Issue 1: API Key Permissions

**Affected Versions**: All
**Symptom**: 403 Forbidden errors on certain operations
**Cause**: Insufficient API key permissions
**Solution**: Ensure API key has appropriate permissions for the operations you need

```python
# Test permissions
try:
    pages = client.pages.list()  # Requires read permission
    client.pages.create(...)      # Requires write permission
    client.users.list()           # Requires admin permission
except PermissionError as e:
    print(f"Permission denied: {e}")
```

### Issue 2: GraphQL Rate Limiting

**Affected Versions**: 2.4+
**Symptom**: 429 Too Many Requests
**Cause**: Too many API calls in short time
**Solution**: Use SDK's built-in retry logic or implement rate limiting

```python
from wikijs import WikiJSClient
from wikijs.cache import MemoryCache

# Enable caching to reduce API calls
cache = MemoryCache(ttl=300)
client = WikiJSClient(
    'https://wiki.example.com',
    auth='your-api-key',
    cache=cache
)
```

### Issue 3: Large File Uploads

**Affected Versions**: All
**Symptom**: Timeout or memory errors on large asset uploads
**Cause**: Default timeout too short for large files
**Solution**: Increase timeout for upload operations

```python
# Increase timeout for large uploads
client = WikiJSClient(
    'https://wiki.example.com',
    auth='your-api-key',
    timeout=300  # 5 minutes
)

# Upload large file
with open('large-file.pdf', 'rb') as f:
    asset = client.assets.upload(f, folder_id=1)
```

---

## 📊 Compatibility Testing

### How We Test Compatibility

1. **Unit Tests**: Test against mocked API responses
2. **Integration Tests**: Test against live Wiki.js 2.5.x instance
3. **Manual Testing**: Periodic testing against 2.4.x and 2.3.x
4. **Community Reports**: User feedback on different versions

### Running Compatibility Tests

```bash
# Run full test suite
pytest

# Run integration tests only
pytest -m integration

# Run with specific Wiki.js version
WIKIJS_VERSION=2.5.308 pytest -m integration
```

### Reporting Compatibility Issues

If you encounter compatibility issues:

1. **Check this guide** for known issues
2. **Verify Wiki.js version**: Ensure you're running 2.2+
3. **Test with examples**: Try SDK examples first
4. **Report issue**: Include Wiki.js version, SDK version, and error details

---

## 🔮 Future Compatibility

### Planned Support

| Version | Status | Timeline |
|---------|--------|----------|
| **Wiki.js 2.6+** | ✅ Planned | Automatic (same API) |
| **Wiki.js 3.0** | 📅 Future | When 3.0 reaches beta |
| **Backward Compat** | ✅ Committed | Will maintain 2.x support |

### Migration Strategy for 3.x

When Wiki.js 3.x becomes stable:

1. **Dual Support**: Maintain both 2.x and 3.x compatibility
2. **Version Detection**: Auto-detect Wiki.js version
3. **Clear Documentation**: Migration guide for 3.x users
4. **Gradual Transition**: Long deprecation period for 2.x

Example future API:

```python
# Future: Automatic version detection
from wikijs import WikiJSClient

# Will work with both 2.x and 3.x
client = WikiJSClient('https://wiki.example.com', auth='key')

# Or force specific version
from wikijs.v2 import WikiJSClient as WikiJSClientV2
from wikijs.v3 import WikiJSClient as WikiJSClientV3

client_v2 = WikiJSClientV2(...)  # Force 2.x API
client_v3 = WikiJSClientV3(...)  # Force 3.x API
```

---

## 📞 Support

### Getting Help

- **Documentation**: [Full documentation](../README.md)
- **Examples**: [Usage examples](../examples/)
- **Issues**: [Report compatibility issues](https://github.com/l3ocho/py-wikijs/issues)

### Resources

- **Wiki.js Documentation**: https://docs.requarks.io/
- **Wiki.js Releases**: https://docs.requarks.io/releases
- **Wiki.js GraphQL API**: https://docs.requarks.io/dev/api
- **Community Forum**: https://github.com/requarks/wiki/discussions

---

## 📝 Version History

| SDK Version | Min Wiki.js | Max Wiki.js | Notes |
|-------------|-------------|-------------|-------|
| **0.1.0** | 2.2 | 2.5.308+ | Initial release |
| **0.2.0** | 2.2 | 2.5.308+ | Added async support |

---

**Last Updated**: October 2025
**Next Review**: When Wiki.js 3.0 beta is released

For the latest compatibility information, always check this guide or visit the [project repository](https://github.com/l3ocho/py-wikijs).
