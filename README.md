# Wiki.js Python SDK

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Support](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Wiki.js Support](https://img.shields.io/badge/Wiki.js-2.2+-green.svg)](https://docs.requarks.io/releases)
[![PyPI Package](https://img.shields.io/badge/PyPI-py--wikijs-blue.svg)](https://pypi.org/project/py-wikijs/)
[![GitHub](https://img.shields.io/badge/GitHub-l3ocho/py--wikijs-blue.svg)](https://github.com/l3ocho/py-wikijs)

**A professional Python SDK for Wiki.js API integration.**

> **🎉 Status**: Phase 1 MVP Complete! Ready for production use
> **Current Version**: v0.1.0 with complete Wiki.js Pages API integration
> **Next Milestone**: v0.2.0 with Users, Groups, and Assets API support

---

## 🚀 Quick Start

### Installation
```bash
# Install from PyPI (recommended)
pip install py-wikijs

# Or install from GitHub
pip install git+https://github.com/l3ocho/py-wikijs.git

# Or clone and install locally for development
git clone https://github.com/l3ocho/py-wikijs.git
cd py-wikijs
pip install -e ".[dev]"
```

### Basic Usage
```python
from wikijs import WikiJSClient

# Initialize client
client = WikiJSClient('https://wiki.example.com', auth='your-api-key')

# List pages
pages = client.pages.list()

# Get a specific page
page = client.pages.get(123)

# Create a new page
from wikijs.models import PageCreate
new_page = client.pages.create(PageCreate(
    title="Getting Started",
    path="getting-started",
    content="# Welcome\n\nThis is your first page!"
))
```

---

## 📋 Requirements

### System Requirements
- **Python**: 3.8 or higher
- **Wiki.js**: 2.2 or higher (tested with 2.5.x series)
- **API Access**: Valid API key with appropriate permissions

### Compatibility Notes
> **✅ Supported**: This SDK is designed for **Wiki.js 2.x** (versions 2.2 through 2.5.308+)
> **⚠️ Not Supported**: Wiki.js 3.x (alpha) uses a different API schema and is not yet supported

For detailed compatibility information, see [docs/compatibility.md](docs/compatibility.md).

---

## ✨ Production Features

### Structured Logging
```python
from wikijs import WikiJSClient
import logging

# Enable detailed logging
client = WikiJSClient(
    'https://wiki.example.com',
    auth='your-api-key',
    log_level=logging.DEBUG
)
```
📚 [Logging Guide](docs/logging.md)

### Metrics & Telemetry
```python
# Get performance metrics
metrics = client.get_metrics()
print(f"Total requests: {metrics['total_requests']}")
print(f"Error rate: {metrics['error_rate']:.2f}%")
print(f"P95 latency: {metrics['latency']['p95']:.2f}ms")
```
📚 [Metrics Guide](docs/metrics.md)

### Rate Limiting
```python
# Prevent API throttling
client = WikiJSClient(
    'https://wiki.example.com',
    auth='your-api-key',
    rate_limit=10.0  # 10 requests/second
)
```
📚 [Rate Limiting Guide](docs/rate_limiting.md)

---

## 🎯 Current Development Status

### **Phase 1: MVP Development** ✅ **COMPLETE**
- ✅ **Complete**: Professional-grade Wiki.js Python SDK
- 🎯 **Goal**: Basic Wiki.js integration with Pages API
- 📦 **Deliverable**: Installable package with core functionality

| Component | Status | Description |
|-----------|--------|-------------|
| **Project Setup** | ✅ Complete | Repository structure, packaging, CI/CD |
| **Core Client** | ✅ Complete | HTTP client with authentication and retry logic |
| **Pages API** | ✅ Complete | Full CRUD operations for wiki pages |
| **Production Features** | ✅ Complete | Logging, metrics, rate limiting |
| **Testing** | ✅ Complete | 85%+ test coverage with comprehensive test suite |
| **Documentation** | ✅ Complete | Complete API reference, user guide, and examples |
| **Security** | ✅ Complete | SECURITY.md policy and best practices |

### **Planned Features**
- **v0.2.0**: Complete API coverage (Users, Groups, Assets)
- **v0.3.0**: Production features (retry logic, caching, monitoring)
- **v1.0.0**: Enterprise features (async support, plugins, advanced CLI)

---

## 📚 Documentation

### **For Users**
- **[Quick Start](#quick-start)**: Basic setup and usage
- **[Requirements](#requirements)**: System and Wiki.js version requirements
- **[Compatibility Guide](docs/compatibility.md)**: Detailed version compatibility information
- **[API Reference](docs/api_reference.md)**: Complete SDK documentation
- **[User Guide](docs/user_guide.md)**: Comprehensive usage guide with examples
- **[Examples](examples/)**: Real-world usage examples and code samples

### **For Contributors**
- **[Contributing Guide](docs/CONTRIBUTING.md)**: How to contribute to the project
- **[Development Guide](docs/development.md)**: Setup and development workflow
- **[Changelog](docs/CHANGELOG.md)**: Version history and changes

### **For Maintainers**
- **[Architecture](docs/wikijs_sdk_architecture.md)**: Technical design and patterns
- **[Development Plan](docs/wikijs_sdk_release_plan.md)**: Complete roadmap and milestones
- **[Development Notes](CLAUDE.md)**: Development workflow and coordination

---

## 🤝 Contributing

We welcome contributions! This project showcases systematic development with professional standards.

**Getting Started:**
1. Check our [Development Plan](docs/wikijs_sdk_release_plan.md) for current priorities
2. Review the [Architecture](docs/wikijs_sdk_architecture.md) for technical context
3. See [Development Notes](CLAUDE.md) for development workflow
4. Start with issues labeled `good first issue` *(Coming soon)*

**Community:**
- 💬 **GitHub Discussions**: Questions and community chat *(Coming soon)*
- 🐛 **GitHub Issues**: Bug reports and feature requests *(Coming soon)*

---

## 🛠️ Development Setup

### Prerequisites
See [Requirements](#requirements) for system and Wiki.js version requirements.

Additional development tools:
- Git
- Wiki.js 2.x instance for testing (2.2 or higher)

### Local Development
```bash
# Clone and setup
git clone https://github.com/l3ocho/py-wikijs.git
cd py-wikijs
pip install -e ".[dev]"

# Run tests
pytest

# Run quality checks
pre-commit run --all-files
```

---

## 🏆 Project Features

### **Current Features**
- ✅ **Core SDK**: Synchronous HTTP client with connection pooling and retry logic
- ✅ **Authentication**: Multiple methods (API key, JWT, custom)
- ✅ **Complete API Coverage**: Pages, Users, Groups, and Assets APIs
- ✅ **Async Support**: Full async/await implementation with `aiohttp`
- ✅ **Intelligent Caching**: LRU cache with TTL support for performance
- ✅ **Batch Operations**: Efficient `create_many`, `update_many`, `delete_many` methods
- ✅ **Auto-Pagination**: `iter_all()` methods for seamless pagination
- ✅ **Error Handling**: Comprehensive exception hierarchy with specific error types
- ✅ **Type Safety**: Pydantic models with full validation
- ✅ **Production Features**: Structured logging, metrics, rate limiting
- ✅ **Testing**: 87%+ test coverage with 270+ tests
- ✅ **Documentation**: Complete API reference, user guide, and examples
- ✅ **Security**: Security policy and vulnerability reporting

### **Planned Enhancements**
- 💻 Advanced CLI tools with interactive mode
- 🔧 Plugin system for extensibility
- 🛡️ Enhanced security features and audit logging
- 🔄 Circuit breaker for fault tolerance
- 📊 Performance monitoring and metrics

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- **Wiki.js**: The excellent knowledge management platform this SDK supports
- **leomiranda**: Developer who created this SDK
- **Python Community**: For exceptional tools and development standards

---

**Ready to contribute?** Check out our [development documentation](docs/) or explore the [development workflow](CLAUDE.md) to see how this project is built!
