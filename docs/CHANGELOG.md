# Changelog

All notable changes to the Wiki.js Python SDK will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Project foundation and repository structure
- Python packaging configuration (setup.py, pyproject.toml)
- CI/CD pipeline with GitHub Actions
- Code quality tools (black, isort, flake8, mypy, bandit)
- Comprehensive documentation structure
- Contributing guidelines and community governance
- Issue and PR templates for GitHub

### Changed
- N/A

### Deprecated
- N/A

### Removed
- N/A

### Fixed
- N/A

### Security
- Added automated security scanning with bandit

## Release Planning

### [0.1.0] - Target: 2 weeks from start
**MVP Release - Basic Wiki.js Integration**

#### Planned Features
- Core WikiJSClient with HTTP transport
- API key authentication
- Pages API with full CRUD operations (list, get, create, update, delete)
- Type-safe data models with Pydantic
- Comprehensive error handling
- >85% test coverage
- Complete API documentation
- GitHub release publication

#### Success Criteria
- [ ] Package installable via `pip install git+https://github.com/...`
- [ ] Basic page operations work with real Wiki.js instance
- [ ] All quality gates pass (tests, coverage, linting, security)
- [ ] Documentation sufficient for basic usage

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