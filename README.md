# Wiki.js Python SDK

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python Support](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![Repository](https://img.shields.io/badge/repo-Gitea-green.svg)](https://gitea.hotserv.cloud/lmiranda/wikijs-sdk-python)
[![Issues](https://img.shields.io/badge/issues-Gitea-blue.svg)](https://gitea.hotserv.cloud/lmiranda/wikijs-sdk-python/issues)

**A professional Python SDK for Wiki.js API integration.**

> **🎉 Status**: Phase 1 MVP Complete! Ready for production use  
> **Current Version**: v0.1.0 with complete Wiki.js Pages API integration
> **Next Milestone**: v0.2.0 with Users, Groups, and Assets API support

---

## 🚀 Quick Start

### Installation
```bash
# Install directly from Gitea
pip install git+https://gitea.hotserv.cloud/lmiranda/wikijs-sdk-python.git

# Or clone and install locally
git clone https://gitea.hotserv.cloud/lmiranda/wikijs-sdk-python.git
cd wikijs-python-sdk
pip install -e .
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
| **Testing** | ✅ Complete | 87%+ test coverage with comprehensive test suite |
| **Documentation** | ✅ Complete | Complete API reference, user guide, and examples |

### **Planned Features**
- **v0.2.0**: Complete API coverage (Users, Groups, Assets)
- **v0.3.0**: Production features (retry logic, caching, monitoring)
- **v1.0.0**: Enterprise features (async support, plugins, advanced CLI)

---

## 📚 Documentation

### **For Users**
- **[Quick Start](#quick-start)**: Basic setup and usage
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
- Python 3.8+
- Git
- Wiki.js instance for testing

### Local Development
```bash
# Clone and setup
git clone https://gitea.hotserv.cloud/lmiranda/wikijs-sdk-python.git
cd wikijs-python-sdk
pip install -e ".[dev]"

# Run tests
pytest

# Run quality checks
pre-commit run --all-files
```

---

## 🏆 Project Features

### **Current (MVP Complete)**
- ✅ Synchronous HTTP client with connection pooling and retry logic
- ✅ Multiple authentication methods (API key, JWT, custom)
- ✅ Complete Pages API with CRUD operations, search, and filtering
- ✅ Comprehensive error handling with specific exception types
- ✅ Type-safe models with validation using Pydantic
- ✅ Extensive test coverage (87%+) with robust test suite
- ✅ Complete documentation with API reference and user guide
- ✅ Practical examples and code samples

### **Planned Enhancements**
- ⚡ Async/await support
- 💾 Intelligent caching
- 🔄 Retry logic with backoff
- 💻 CLI tools
- 🔧 Plugin system
- 🛡️ Advanced security features

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