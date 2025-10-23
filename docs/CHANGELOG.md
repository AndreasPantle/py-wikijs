# Changelog

All notable changes to the Wiki.js Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- N/A

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- N/A

---

## [0.1.0] - 2025-10-23
**MVP Release - Basic Wiki.js Integration** ✅

This is the first production-ready release of the Wiki.js Python SDK, delivering a complete, professional-grade SDK for Wiki.js Pages API integration.

### Added

#### Core Implementation
- **WikiJSClient**: Complete HTTP client with connection pooling and automatic retry logic
  - Configurable timeout, SSL verification, and custom User-Agent support
  - Context manager support for automatic resource cleanup
  - Connection testing via GraphQL queries
- **Authentication System**: Three authentication methods
  - `NoAuth`: For testing and public instances
  - `APIKeyAuth`: API key-based authentication with Bearer tokens
  - `JWTAuth`: JWT token authentication with automatic refresh capability
- **Pages API**: Full CRUD operations (679 lines of implementation)
  - `list()`: List pages with filtering, pagination, search, and sorting
  - `get()`: Get page by ID
  - `get_by_path()`: Get page by path with locale support
  - `create()`: Create new pages with full metadata
  - `update()`: Update existing pages (partial updates supported)
  - `delete()`: Delete pages
  - `search()`: Full-text search across pages
  - `get_by_tags()`: Filter pages by tags
- **Data Models**: Pydantic-based type-safe models
  - `Page`: Complete page representation with computed properties (word_count, reading_time, url_path)
  - `PageCreate`: Page creation with validation
  - `PageUpdate`: Partial page updates
  - Methods: `extract_headings()`, `has_tag()`
- **Exception Hierarchy**: 11 exception types for precise error handling
  - Base: `WikiJSException`
  - API: `APIError`, `ClientError`, `ServerError`
  - Specific: `NotFoundError`, `PermissionError`, `RateLimitError`
  - Auth: `AuthenticationError`, `ConfigurationError`
  - Connection: `ConnectionError`, `TimeoutError`
  - Validation: `ValidationError`
- **Utilities**: Helper functions (223 lines)
  - URL normalization and validation
  - Path sanitization
  - Response parsing and error extraction
  - Safe dictionary access and list chunking

#### Quality Infrastructure
- **Test Suite**: 2,641 lines of test code
  - 231 test functions across 11 test files
  - 87%+ code coverage achieved
  - Unit, integration, and E2E tests
  - Comprehensive fixture system
- **Code Quality Tools**:
  - Black for code formatting
  - isort for import sorting
  - flake8 for linting
  - mypy for type checking (strict mode)
  - bandit for security scanning
  - pre-commit hooks configured
- **CI/CD**: Gitea Actions pipelines ready
  - Automated testing on push
  - Quality gate enforcement
  - Release automation

#### Documentation (3,589+ lines)
- **User Documentation**:
  - Complete API Reference
  - Comprehensive User Guide with examples
  - Quick Start guide in README
- **Developer Documentation**:
  - Contributing guidelines
  - Development guide with workflow
  - Architecture documentation
  - Release planning documentation
- **Governance**:
  - Community governance charter
  - Risk management framework
  - Code of conduct
- **Examples**:
  - `basic_usage.py`: Fundamental operations (170 lines)
  - `content_management.py`: Advanced patterns (429 lines)
  - Examples README with scenarios

#### Project Infrastructure
- Project foundation and repository structure
- Python packaging configuration (setup.py, pyproject.toml)
- Dependency management (requirements.txt, requirements-dev.txt)
- Git configuration and .gitignore
- Issue and PR templates
- License (MIT)

### Changed
- N/A (initial release)

### Deprecated
- N/A (initial release)

### Removed
- N/A (initial release)

### Fixed
- N/A (initial release)

### Security
- Automated security scanning with bandit
- Input validation on all public APIs
- No hardcoded credentials or secrets
- SSL certificate verification enabled by default
- API key masking in logs

## Release Planning

### [0.1.0] - Released: 2025-10-23 ✅
**MVP Release - Basic Wiki.js Integration - COMPLETE**

#### Delivered Features ✅
- ✅ Core WikiJSClient with HTTP transport
- ✅ Three authentication methods (NoAuth, API Key, JWT)
- ✅ Pages API with full CRUD operations (list, get, create, update, delete)
- ✅ Additional operations: search, get_by_path, get_by_tags
- ✅ Type-safe data models with Pydantic
- ✅ Comprehensive error handling (11 exception types)
- ✅ 87%+ test coverage (231 tests)
- ✅ Complete API documentation (3,589+ lines)
- ✅ Gitea release publication

#### Success Criteria - ALL MET ✅
- [x] Package installable via `pip install git+https://gitea.hotserv.cloud/lmiranda/wikijs-sdk-python.git`
- [x] Basic page operations work with real Wiki.js instance
- [x] All quality gates pass (tests, coverage, linting, security)
- [x] Documentation sufficient for basic usage
- [x] Examples provided (basic_usage.py, content_management.py)

### [0.2.0] - Target: 4 weeks from start
**Essential Features - Complete API Coverage**

#### Planned Features
- Users API (full CRUD operations)
- Groups API (management and permissions)
- Assets API (file upload and management)
- System API (health checks and info)
- Enhanced error handling with detailed context
- Configuration management (file and environment-based)
- Basic CLI interface
- Performance benchmarks

### [0.3.0] - Target: 7 weeks from start
**Production Ready - Reliability & Performance**

#### Planned Features
- Retry logic with exponential backoff
- Circuit breaker for fault tolerance
- Intelligent caching with multiple backends
- Rate limiting and API compliance
- Performance monitoring and metrics
- Bulk operations for efficiency
- Connection pooling optimization

### [1.0.0] - Target: 11 weeks from start
**Enterprise Grade - Advanced Features**

#### Planned Features
- Full async/await support with aiohttp
- Advanced CLI with interactive mode
- Plugin architecture for extensibility
- Advanced authentication (JWT rotation, OAuth2)
- Enterprise security features
- Webhook support and verification
- Multi-tenancy support

---

## Development Notes

### Versioning Strategy
- **MAJOR**: Breaking changes that require user action
- **MINOR**: New features that are backward compatible
- **PATCH**: Bug fixes and improvements that are backward compatible

### Quality Standards
All releases must meet:
- [ ] >85% test coverage (>90% for minor releases)
- [ ] 100% type coverage on public APIs
- [ ] All quality gates pass (linting, formatting, security)
- [ ] Complete documentation for new features
- [ ] No known critical bugs

### Community Involvement
- Feature requests welcomed through GitHub issues
- Community feedback incorporated into release planning
- Breaking changes require community discussion period
- Beta releases available for testing major features

---

*This changelog is maintained as part of our commitment to transparency and professional development practices. All changes are documented to help users understand what's new, what's changed, and how to upgrade safely.*