# Contributing to Wiki.js Python SDK

Thank you for your interest in contributing to the Wiki.js Python SDK! This guide will help you get started with contributing to this community-driven project.

## 🎯 Project Context

This project was developed by leomiranda, showcasing professional development practices while building a production-ready SDK for Wiki.js. We welcome contributors of all experience levels!

**Current Status**: MVP Development (Phase 1)  
**Focus**: Core functionality and foundational quality

## 🚀 Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- A GitHub account
- (Optional) A Wiki.js instance for testing

### Development Setup

1. **Fork the Repository**
   ```bash
   # Fork on GitHub, then clone your fork
   git clone https://github.com/yourusername/wikijs-python-sdk.git
   cd wikijs-python-sdk
   ```

2. **Set Up Development Environment**
   ```bash
   # Create virtual environment
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   
   # Install in development mode
   pip install -e ".[dev]"
   
   # Install pre-commit hooks
   pre-commit install
   ```

3. **Verify Setup**
   ```bash
   # Run tests
   pytest
   
   # Run quality checks
   pre-commit run --all-files
   ```

## 📋 Development Process

### Finding Work

1. **Check Current Priorities**
   - Review [CLAUDE.md](CLAUDE.md) for current development tasks
   - See [Development Plan](docs/wikijs_sdk_release_plan.md) for roadmap
   - Look for issues labeled `good first issue`

2. **Understand Architecture**
   - Read [Architecture Overview](docs/wikijs_sdk_architecture.md)
   - Review existing code patterns
   - Check the [Risk Management](docs/RISK_MANAGEMENT.md) for known issues

### Making Changes

1. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Follow Code Standards**
   - Write type hints for all public APIs
   - Add docstrings to all public methods (Google style)
   - Follow existing code patterns
   - Keep functions small and focused

3. **Write Tests**
   - Add unit tests for new functionality
   - Maintain >85% code coverage
   - Use descriptive test names
   - Include edge cases

4. **Update Documentation**
   - Update docstrings for changed methods
   - Add examples for new features
   - Update README if needed

### Code Quality Standards

#### Python Style
```python
def example_function(param: str, optional: Optional[int] = None) -> bool:
    """Example function following our standards.
    
    Args:
        param: Description of the parameter
        optional: Optional parameter with default
        
    Returns:
        Boolean result of the operation
        
    Raises:
        ValueError: If param is empty
        
    Example:
        >>> example_function("test")
        True
    """
    if not param:
        raise ValueError("param cannot be empty")
    
    # Implementation here
    return True
```

#### Testing Patterns
```python
import pytest
from wikijs import WikiJSClient
from wikijs.exceptions import WikiJSException

class TestWikiJSClient:
    """Test WikiJS client functionality."""
    
    def test_client_initialization_success(self):
        """Test successful client initialization."""
        client = WikiJSClient("https://wiki.example.com", "api-key")
        assert client.base_url == "https://wiki.example.com"
    
    def test_client_initialization_invalid_url(self):
        """Test client initialization with invalid URL."""
        with pytest.raises(ValueError, match="Invalid URL"):
            WikiJSClient("invalid-url", "api-key")
```

### Submitting Changes

1. **Run Quality Checks**
   ```bash
   # Format code
   black wikijs tests
   isort wikijs tests
   
   # Run linting
   flake8 wikijs tests
   mypy wikijs
   
   # Run tests
   pytest --cov=wikijs --cov-fail-under=85
   
   # Security scan
   bandit -r wikijs
   ```

2. **Commit Changes**
   ```bash
   git add .
   git commit -m "feat: add new feature description
   
   Detailed description of what was changed and why.
   
   Closes #123"
   ```

3. **Create Pull Request**
   - Push to your fork
   - Create PR against `main` branch
   - Fill out the PR template completely
   - Link related issues

## 🤝 Community Guidelines

### Communication
- **Be respectful** and constructive in all interactions
- **Ask questions** if anything is unclear
- **Help others** when you can
- **Focus on the code**, not the person

### Code Review Process
1. **Maintainer Review**: All PRs reviewed by project maintainer
2. **Feedback**: Address review comments promptly
3. **Discussion**: Open discussion encouraged for design decisions
4. **Approval**: PR approved when all checks pass and review complete

### Response Times
- **Issues**: Response within 48-72 hours
- **Pull Requests**: Initial review within 1 week
- **Questions**: Community-driven with maintainer backup

## 🏗️ Architecture & Patterns

### Project Structure
```
wikijs/
├── __init__.py          # Package entry point
├── client.py            # Main client class
├── exceptions.py        # Exception hierarchy
├── models/              # Data models (Pydantic)
├── auth/                # Authentication handlers
├── endpoints/           # API endpoint implementations
└── utils/               # Utility functions
```

### Key Patterns
- **Dependency Injection**: Use abstract interfaces
- **Type Safety**: Full type hints and validation
- **Error Handling**: Comprehensive exception hierarchy
- **Testing**: Mock external dependencies
- **Documentation**: Example-driven docstrings

## 🧪 Testing Guidelines

### Test Categories
- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test component interactions
- **End-to-End**: Test with real Wiki.js instance (CI only)

### Test Organization
```
tests/
├── unit/
│   ├── test_client.py
│   ├── test_models.py
│   └── test_auth.py
├── integration/
│   └── test_api_endpoints.py
└── conftest.py          # Shared fixtures
```

### Writing Good Tests
```python
def test_specific_behavior_with_expected_outcome():
    """Test description should be clear and specific."""
    # Arrange
    client = WikiJSClient("https://example.com", "key")
    
    # Act
    result = client.some_method()
    
    # Assert
    assert result.expected_property == "expected_value"
```

## 🐛 Bug Reports

### Before Reporting
1. Check existing issues
2. Test with latest version
3. Provide minimal reproduction case

### Bug Report Checklist
- [ ] Clear description of the problem
- [ ] Steps to reproduce
- [ ] Expected vs actual behavior
- [ ] Environment details
- [ ] Error messages/stack traces
- [ ] Minimal code example

## ✨ Feature Requests

### Before Requesting
1. Check if feature already exists
2. Search existing feature requests
3. Consider if it fits project scope

### Feature Request Checklist
- [ ] Clear use case description
- [ ] Proposed API design
- [ ] Implementation considerations
- [ ] Breaking change analysis

## 🚢 Release Process

Releases are managed by maintainers:

1. **Version Bump**: Update version in `wikijs/version.py`
2. **Changelog**: Update `CHANGELOG.md` with changes
3. **Tag Release**: Create git tag `v0.1.0`
4. **Automated**: GitHub Actions handles testing and GitHub release creation

## 📚 Documentation

### Types of Documentation
- **API Reference**: Auto-generated from docstrings
- **User Guides**: How-to guides and tutorials
- **Examples**: Real-world usage examples
- **Architecture**: Technical design decisions

### Documentation Standards
- Write for your audience (users vs contributors)
- Include practical examples
- Keep it up-to-date with code changes
- Use clear, concise language

## 📋 Development Context

This project was developed by leomiranda with careful coordination and planning. If you're interested in the development process:

- See [CLAUDE.md](CLAUDE.md) for development coordination details
- Development tasks are tracked and managed systematically
- Quality standards are maintained through automated tooling
- Community contributions are integrated with systematic development processes

## ❓ Getting Help

### Questions and Support
- **GitHub Discussions**: General questions and community chat
- **GitHub Issues**: Bug reports and feature requests
- **Documentation**: Check docs for existing answers
- **Code Review**: Learn through the review process

### Common Questions

**Q: How do I set up a test Wiki.js instance?**
A: Check the testing documentation for local setup instructions.

**Q: What should I work on first?**
A: Look for `good first issue` labels or check CLAUDE.md for current priorities.

**Q: How do I add a new API endpoint?**
A: Follow the existing patterns in `wikijs/endpoints/` and add corresponding tests.

## 🙏 Recognition

All contributors are recognized in:
- `CONTRIBUTORS.md` file
- Release notes for significant contributions
- GitHub contributors page

Significant contributors may be invited to become maintainers.

---

**Ready to contribute?** 

1. Read our [Governance](docs/GOVERNANCE.md) guidelines
2. Check the [current development status](CLAUDE.md)
3. Look for [good first issues](https://github.com/yourusername/wikijs-python-sdk/labels/good%20first%20issue)
4. Join the discussion!

**Questions?** Don't hesitate to ask in [GitHub Discussions](https://github.com/yourusername/wikijs-python-sdk/discussions) or create an issue.