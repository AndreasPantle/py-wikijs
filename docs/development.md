# Development Guide

Guide for contributors and developers working on the Wiki.js Python SDK.

## Table of Contents

- [Development Setup](#development-setup)
- [Project Structure](#project-structure)
- [Development Workflow](#development-workflow)
- [Testing](#testing)
- [Code Quality](#code-quality)
- [Documentation](#documentation)
- [Release Process](#release-process)

---

## Development Setup

### Prerequisites

- **Python 3.8+** (tested with 3.8, 3.9, 3.10, 3.11, 3.12)
- **Git** for version control
- **Wiki.js instance** for testing (can be local or remote)

### Environment Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yourusername/py-wikijs.git
   cd py-wikijs
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install development dependencies:**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Set up pre-commit hooks:**
   ```bash
   pre-commit install
   ```

5. **Configure environment variables:**
   ```bash
   export WIKIJS_URL='https://your-test-wiki.example.com'
   export WIKIJS_API_KEY='your-test-api-key'
   ```

### Verify Setup

```bash
# Run tests
pytest

# Check code quality
pre-commit run --all-files

# Verify package can be imported
python -c "from wikijs import WikiJSClient; print('✅ Setup successful!')"
```

---

## Project Structure

```
py-wikijs/
├── wikijs/                    # Main package
│   ├── __init__.py           # Package exports
│   ├── version.py            # Version information
│   ├── client.py             # Main WikiJS client
│   ├── exceptions.py         # Exception classes
│   ├── auth/                 # Authentication handlers
│   │   ├── __init__.py       # Auth exports
│   │   ├── base.py           # Base auth handler
│   │   ├── api_key.py        # API key authentication
│   │   └── jwt.py            # JWT authentication
│   ├── endpoints/            # API endpoints
│   │   ├── __init__.py       # Endpoint exports
│   │   ├── base.py           # Base endpoint class
│   │   └── pages.py          # Pages API endpoint
│   ├── models/               # Data models
│   │   ├── __init__.py       # Model exports
│   │   ├── base.py           # Base model classes
│   │   └── page.py           # Page-related models
│   └── utils/                # Utility functions
│       ├── __init__.py       # Utility exports
│       └── helpers.py        # Helper functions
├── tests/                    # Test suite
│   ├── conftest.py          # Test configuration
│   ├── auth/                # Authentication tests
│   ├── endpoints/           # Endpoint tests
│   ├── models/              # Model tests
│   └── utils/               # Utility tests
├── docs/                    # Documentation
│   ├── api_reference.md     # API reference
│   ├── user_guide.md        # User guide
│   ├── development.md       # This file
│   └── ...
├── examples/                # Usage examples
├── .gitea/                  # Gitea workflows
│   └── workflows/           # CI/CD pipelines
├── pyproject.toml          # Project configuration
├── setup.py                # Package setup
├── requirements.txt        # Runtime dependencies
├── requirements-dev.txt    # Development dependencies
└── README.md               # Project README
```

### Key Components

#### **Client (`wikijs/client.py`)**
- Main entry point for the SDK
- Manages HTTP sessions and requests
- Handles authentication and error handling
- Provides access to endpoint handlers

#### **Authentication (`wikijs/auth/`)**
- Base authentication handler interface
- Concrete implementations for API key and JWT auth
- Extensible for custom authentication methods

#### **Endpoints (`wikijs/endpoints/`)**
- API endpoint implementations
- Each endpoint handles a specific Wiki.js API area
- Base endpoint class provides common functionality

#### **Models (`wikijs/models/`)**
- Pydantic models for data validation and serialization
- Type-safe data structures
- Input validation and error handling

#### **Utilities (`wikijs/utils/`)**
- Helper functions for common operations
- URL handling, response parsing, etc.
- Shared utility functions

---

## Development Workflow

### Branch Strategy

- **`main`**: Stable, production-ready code
- **`develop`**: Integration branch for new features
- **Feature branches**: `feature/description` for new features
- **Bug fixes**: `fix/description` for bug fixes
- **Hotfixes**: `hotfix/description` for critical fixes

### Workflow Steps

1. **Create a feature branch:**
   ```bash
   git checkout -b feature/new-awesome-feature
   ```

2. **Make your changes:**
   - Write code following our style guidelines
   - Add tests for new functionality
   - Update documentation as needed

3. **Run quality checks:**
   ```bash
   # Run tests
   pytest
   
   # Check code formatting
   black --check .
   
   # Check imports
   isort --check-only .
   
   # Type checking
   mypy wikijs
   
   # Linting
   flake8 wikijs
   
   # Security scan
   bandit -r wikijs
   ```

4. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add awesome new feature"
   ```

5. **Push and create PR:**
   ```bash
   git push origin feature/new-awesome-feature
   # Create pull request on GitHub
   ```

### Commit Message Format

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

**Types:**
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that don't affect code meaning
- `refactor`: Code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests or correcting existing tests
- `chore`: Other changes that don't modify src or test files

**Examples:**
```
feat(auth): add JWT authentication support
fix(client): handle connection timeout properly
docs: update API reference for pages endpoint
test: add comprehensive model validation tests
```

---

## Testing

### Test Organization

- **Unit tests**: Test individual components in isolation
- **Integration tests**: Test component interactions
- **End-to-end tests**: Test complete workflows
- **Mock tests**: Test with mocked external dependencies

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=wikijs --cov-report=html

# Run specific test file
pytest tests/test_client.py

# Run specific test
pytest tests/test_client.py::TestWikiJSClient::test_basic_initialization

# Run tests with verbose output
pytest -v

# Run tests and stop on first failure
pytest -x
```

### Writing Tests

#### Test Structure

```python
"""Tests for module_name."""

import pytest
from unittest.mock import Mock, patch

from wikijs.module_name import ClassUnderTest
from wikijs.exceptions import SomeException


class TestClassUnderTest:
    """Test suite for ClassUnderTest."""
    
    @pytest.fixture
    def sample_data(self):
        """Sample data for testing."""
        return {"key": "value"}
    
    def test_basic_functionality(self, sample_data):
        """Test basic functionality."""
        # Arrange
        instance = ClassUnderTest()
        
        # Act
        result = instance.some_method(sample_data)
        
        # Assert
        assert result is not None
        assert result.key == "value"
    
    def test_error_handling(self):
        """Test proper error handling."""
        instance = ClassUnderTest()
        
        with pytest.raises(SomeException, match="Expected error message"):
            instance.method_that_should_fail()
    
    @patch('wikijs.module_name.external_dependency')
    def test_with_mocking(self, mock_dependency):
        """Test with mocked dependencies."""
        # Setup mock
        mock_dependency.return_value = "mocked result"
        
        # Test
        instance = ClassUnderTest()
        result = instance.method_using_dependency()
        
        # Verify
        assert result == "mocked result"
        mock_dependency.assert_called_once()
```

#### Test Guidelines

1. **Follow AAA pattern**: Arrange, Act, Assert
2. **Use descriptive test names** that explain what is being tested
3. **Test both success and failure cases**
4. **Mock external dependencies** (HTTP requests, file system, etc.)
5. **Use fixtures** for common test data and setup
6. **Maintain high test coverage** (target: >85%)

### Test Configuration

#### `conftest.py`

```python
"""Shared test configuration and fixtures."""

import pytest
from unittest.mock import Mock

from wikijs import WikiJSClient


@pytest.fixture
def mock_client():
    """Create a mock WikiJS client for testing."""
    client = Mock(spec=WikiJSClient)
    client.base_url = "https://test-wiki.example.com"
    return client


@pytest.fixture
def sample_page_data():
    """Sample page data for testing."""
    return {
        "id": 123,
        "title": "Test Page",
        "path": "test-page",
        "content": "# Test\n\nContent here.",
        "is_published": True,
        "tags": ["test"]
    }
```

---

## Code Quality

### Code Style

We use several tools to maintain code quality:

- **Black**: Code formatting
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking
- **bandit**: Security scanning

### Configuration Files

#### `pyproject.toml`

```toml
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88

[tool.mypy]
python_version = "3.8"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "--strict-markers --disable-warnings"
```

### Pre-commit Hooks

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
  
  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
  
  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
  
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.3.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
```

### Quality Checks

Run these commands before committing:

```bash
# Format code
black .
isort .

# Check formatting
black --check .
isort --check-only .

# Lint code
flake8 wikijs tests

# Type checking
mypy wikijs

# Security scan
bandit -r wikijs

# Run all pre-commit hooks
pre-commit run --all-files
```

---

## Documentation

### Documentation Types

1. **API Reference**: Auto-generated from docstrings
2. **User Guide**: Manual documentation for end users
3. **Development Guide**: This document
4. **Examples**: Practical usage examples
5. **Changelog**: Version history and changes

### Writing Documentation

#### Docstring Format

We use Google-style docstrings:

```python
def create_page(self, page_data: PageCreate) -> Page:
    """Create a new page in the wiki.
    
    Args:
        page_data: Page creation data containing title, path, content, etc.
        
    Returns:
        The created Page object with assigned ID and metadata.
        
    Raises:
        ValidationError: If page data is invalid.
        APIError: If the API request fails.
        AuthenticationError: If authentication fails.
        
    Example:
        >>> from wikijs.models import PageCreate
        >>> page_data = PageCreate(
        ...     title="My Page",
        ...     path="my-page",
        ...     content="# Hello World"
        ... )
        >>> created_page = client.pages.create(page_data)
        >>> print(f"Created page with ID: {created_page.id}")
    """
```

#### Documentation Guidelines

1. **Be clear and concise** in explanations
2. **Include examples** for complex functionality
3. **Document all public APIs** with proper docstrings
4. **Keep documentation up to date** with code changes
5. **Use consistent formatting** and style

### Building Documentation

```bash
# Install documentation dependencies
pip install -e ".[docs]"

# Build documentation (if using Sphinx)
cd docs
make html

# Serve documentation locally
python -m http.server 8000 -d _build/html
```

---

## Release Process

### Version Management

We use [Semantic Versioning](https://semver.org/):

- **MAJOR**: Incompatible API changes
- **MINOR**: New functionality (backward compatible)
- **PATCH**: Bug fixes (backward compatible)

### Release Steps

1. **Update version number** in `wikijs/version.py`
2. **Update docs/CHANGELOG.md** with new version details
3. **Run full test suite** and ensure all checks pass
4. **Create release commit**:
   ```bash
   git add .
   git commit -m "chore: bump version to v1.2.3"
   ```
5. **Create and push tag**:
   ```bash
   git tag v1.2.3
   git push origin main --tags
   ```
6. **GitHub Actions** will automatically:
   - Run tests
   - Build package
   - Publish to PyPI
   - Create GitHub release

### Pre-release Checklist

- [ ] All tests pass
- [ ] Code coverage meets requirements (>85%)
- [ ] Documentation is updated
- [ ] docs/CHANGELOG.md is updated
- [ ] Version number is bumped
- [ ] No breaking changes without major version bump
- [ ] Examples work with new version

### Release Automation

Our CI/CD pipeline automatically handles:

- **Testing**: Run test suite on multiple Python versions
- **Quality checks**: Code formatting, linting, type checking
- **Security**: Vulnerability scanning
- **Building**: Create source and wheel distributions
- **Publishing**: Upload to PyPI on tagged releases
- **Documentation**: Update documentation site

---

## Contributing Guidelines

### Getting Started

1. **Fork the repository** on GitHub
2. **Create a feature branch** from `develop`
3. **Make your changes** following our guidelines
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Submit a pull request**

### Pull Request Process

1. **Ensure CI passes** - all tests and quality checks must pass
2. **Update documentation** - include any necessary documentation updates
3. **Add tests** - maintain or improve test coverage
4. **Follow conventions** - use consistent code style and commit messages
5. **Be responsive** - address feedback and review comments promptly

### Code Review Guidelines

As a reviewer:
- **Be constructive** and helpful in feedback
- **Check for correctness** and potential issues
- **Verify tests** cover new functionality
- **Ensure documentation** is adequate
- **Approve when ready** or request specific changes

As an author:
- **Respond promptly** to review feedback
- **Make requested changes** or explain why they're not needed
- **Keep PRs focused** - one feature or fix per PR
- **Test thoroughly** before requesting review

---

## Debugging and Troubleshooting

### Common Development Issues

#### Import Errors

```bash
# Install package in development mode
pip install -e .

# Verify Python path
python -c "import sys; print(sys.path)"
```

#### Test Failures

```bash
# Run specific failing test with verbose output
pytest -xvs tests/path/to/failing_test.py::test_name

# Debug with pdb
pytest --pdb tests/path/to/failing_test.py::test_name
```

#### Type Checking Issues

```bash
# Run mypy on specific file
mypy wikijs/module_name.py

# Show mypy configuration
mypy --config-file
```

### Debugging Tools

#### Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('wikijs')
logger.setLevel(logging.DEBUG)
```

#### Python Debugger

```python
import pdb

# Set breakpoint
pdb.set_trace()

# Or use built-in breakpoint() (Python 3.7+)
breakpoint()
```

#### HTTP Debugging

```python
import http.client

# Enable HTTP debugging
http.client.HTTPConnection.debuglevel = 1
```

---

## Resources

### Useful Links

- **[Wiki.js API Documentation](https://docs.js.wiki/dev/api)** - Official API docs
- **[GraphQL](https://graphql.org/learn/)** - GraphQL learning resources
- **[Pydantic](https://pydantic-docs.helpmanual.io/)** - Data validation library
- **[Requests](https://docs.python-requests.org/)** - HTTP library documentation
- **[pytest](https://docs.pytest.org/)** - Testing framework documentation

### Development Tools

- **VS Code Extensions**: Python, Pylance, Black Formatter, isort
- **PyCharm**: Professional Python IDE
- **Postman**: API testing tool
- **GraphQL Playground**: GraphQL query testing

### Community

- **GitHub Discussions**: Ask questions and share ideas
- **GitHub Issues**: Report bugs and request features
- **Pull Requests**: Contribute code improvements

---

## Questions?

If you have questions about development:

1. **Check this documentation** and the API reference
2. **Search existing issues** on GitHub
3. **Ask in GitHub Discussions** for community help
4. **Create an issue** for bugs or feature requests

Happy coding! 🚀