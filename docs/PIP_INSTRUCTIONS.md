# PyPI Publishing Instructions

This document provides step-by-step instructions for publishing the Wiki.js Python SDK to PyPI.

## Prerequisites

- Package has been built and tested locally
- All tests pass with >85% coverage
- Documentation is complete and up-to-date
- GitHub repository is properly configured

## Pre-Publishing Checklist

### 1. Update Repository URLs
Replace `yourusername` with your actual GitHub username in the following files:

**setup.py** (lines 44, 46-48):
```python
url="https://github.com/YOUR_USERNAME/wikijs-python-sdk",
project_urls={
    "Bug Reports": "https://github.com/YOUR_USERNAME/wikijs-python-sdk/issues",
    "Source": "https://github.com/YOUR_USERNAME/wikijs-python-sdk",
    "Documentation": "https://github.com/YOUR_USERNAME/wikijs-python-sdk/docs",
}
```

**pyproject.toml** (lines 65-68):
```toml
[project.urls]
Homepage = "https://github.com/YOUR_USERNAME/wikijs-python-sdk"
"Bug Reports" = "https://github.com/YOUR_USERNAME/wikijs-python-sdk/issues"
Source = "https://github.com/YOUR_USERNAME/wikijs-python-sdk"
Documentation = "https://github.com/YOUR_USERNAME/wikijs-python-sdk/docs"
```

**README.md** (lines 6-7):
```markdown
[![CI Status](https://github.com/YOUR_USERNAME/wikijs-python-sdk/workflows/Test%20Suite/badge.svg)](https://github.com/YOUR_USERNAME/wikijs-python-sdk/actions)
[![Coverage](https://codecov.io/gh/YOUR_USERNAME/wikijs-python-sdk/branch/main/graph/badge.svg)](https://codecov.io/gh/YOUR_USERNAME/wikijs-python-sdk)
```

### 2. Verify Package Name Availability
Check if `wikijs-python-sdk` is available on PyPI:
- Visit https://pypi.org/project/wikijs-python-sdk/
- If it returns a 404, the name is available
- If needed, update the package name in `setup.py` and `pyproject.toml`

### 3. Version Management
Ensure the version in `wikijs/version.py` reflects the release:
```python
__version__ = "0.1.0"  # Update as needed
```

## PyPI Account Setup

### 1. Create Accounts
Register for both test and production PyPI:
- **Test PyPI**: https://test.pypi.org/account/register/
- **Production PyPI**: https://pypi.org/account/register/

### 2. Generate API Tokens
For each account, create API tokens:
1. Go to Account Settings
2. Navigate to "API tokens"
3. Click "Add API token"
4. Choose scope: "Entire account" (for first upload)
5. Save the token securely

## Publishing Process

### 1. Install Publishing Tools
```bash
pip install twine build
```

### 2. Build the Package
```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info/

# Build the package
python -m build
```

### 3. Validate the Package
```bash
# Check package for common issues
twine check dist/*
```

Expected output:
```
Checking dist/wikijs_python_sdk-0.1.0-py3-none-any.whl: PASSED
Checking dist/wikijs_python_sdk-0.1.0.tar.gz: PASSED
```

### 4. Test Upload (Recommended)
Always test on Test PyPI first:

```bash
# Upload to Test PyPI
twine upload --repository testpypi dist/*
```

When prompted:
- **Username**: `__token__`
- **Password**: Your Test PyPI API token

### 5. Test Installation
```bash
# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ wikijs-python-sdk

# Test basic functionality
python -c "from wikijs import WikiJSClient; print('Import successful')"
```

### 6. Production Upload
Once testing is successful:

```bash
# Upload to production PyPI
twine upload dist/*
```

When prompted:
- **Username**: `__token__`
- **Password**: Your Production PyPI API token

### 7. Verify Production Installation
```bash
# Install from PyPI
pip install wikijs-python-sdk

# Verify installation
python -c "from wikijs import WikiJSClient; print('Production install successful')"
```

## Post-Publishing Tasks

### 1. Update Documentation
- Update README.md installation instructions
- Remove "Coming soon" notes
- Add PyPI badge if desired

### 2. Create GitHub Release
1. Go to your GitHub repository
2. Click "Releases" → "Create a new release"
3. Tag version: `v0.1.0`
4. Release title: `v0.1.0 - MVP Release`
5. Copy changelog content as description
6. Attach built files from `dist/`

### 3. Announce Release
- Update project status in README.md
- Consider posting to relevant communities
- Update project documentation

## Troubleshooting

### Common Issues

**"Package already exists"**
- The package name is taken
- Update package name in configuration files
- Or contact PyPI if you believe you own the name

**"Invalid authentication credentials"**
- Verify you're using `__token__` as username
- Check that the API token is correct and has proper scope
- Ensure the token hasn't expired

**"File already exists"**
- You're trying to upload the same version twice
- Increment the version number in `wikijs/version.py`
- Rebuild the package

**Package validation errors**
- Run `twine check dist/*` for detailed error messages
- Common issues: missing README, invalid metadata
- Fix issues and rebuild

### Getting Help

- **PyPI Help**: https://pypi.org/help/
- **Packaging Guide**: https://packaging.python.org/
- **Twine Documentation**: https://twine.readthedocs.io/

## Automated Publishing (Future)

Consider setting up GitHub Actions for automated publishing:

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    - name: Install dependencies
      run: |
        pip install build twine
    - name: Build package
      run: python -m build
    - name: Publish to PyPI
      env:
        TWINE_USERNAME: __token__
        TWINE_PASSWORD: ${{ secrets.PYPI_API_TOKEN }}
      run: twine upload dist/*
```

## Security Notes

- Never commit API tokens to version control
- Use repository secrets for automated publishing
- Regularly rotate API tokens
- Use scoped tokens when possible
- Monitor package downloads for suspicious activity

---

**Next Steps**: Once published, users can install with `pip install wikijs-python-sdk`