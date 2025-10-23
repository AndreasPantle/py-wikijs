# Deployment Guide - Publishing py-wikijs to PyPI

**Last Updated**: October 2025
**Target Audience**: Maintainers and release managers

---

## 📋 Overview

This guide covers how to build, test, and publish the `py-wikijs` package to PyPI (Python Package Index).

---

## ✅ Pre-Deployment Checklist

### 1. Code Quality
- [ ] All tests pass (`pytest`)
- [ ] Code coverage ≥85% (`pytest --cov`)
- [ ] Linting passes (`black`, `flake8`, `mypy`)
- [ ] Security scan passes (`bandit`)
- [ ] No critical bugs in issue tracker

### 2. Documentation
- [ ] README.md is up to date
- [ ] CHANGELOG.md has release notes
- [ ] API documentation is current
- [ ] Examples are tested and working
- [ ] Compatibility guide is accurate

### 3. Version Management
- [ ] Version bumped in `wikijs/version.py`
- [ ] CHANGELOG.md updated with new version
- [ ] Git tag created for release
- [ ] No uncommitted changes

### 4. Legal & Metadata
- [ ] LICENSE file present (MIT)
- [ ] setup.py metadata correct
- [ ] pyproject.toml metadata correct
- [ ] Author information accurate

---

## 🔧 Prerequisites

### Required Tools

```bash
# Install build and publishing tools
pip install --upgrade pip
pip install build twine
```

### PyPI Account Setup

1. **Create PyPI Account**: https://pypi.org/account/register/
2. **Create API Token**:
   - Go to https://pypi.org/manage/account/
   - Click "Add API token"
   - Name: `py-wikijs-upload`
   - Scope: Entire account (or specific project after first upload)
3. **Save Token Securely**: Store in password manager or environment variable

### Configure PyPI Credentials

**Option 1: Using .pypirc file** (Recommended for local development)

```bash
# Create ~/.pypirc
cat > ~/.pypirc << 'EOF'
[distutils]
index-servers =
    pypi
    testpypi

[pypi]
username = __token__
password = pypi-AgEIcHlwaS5vcmc...YOUR-TOKEN-HERE...

[testpypi]
repository = https://test.pypi.org/legacy/
username = __token__
password = pypi-AgENdGVzdC5weXBp...YOUR-TEST-TOKEN-HERE...
EOF

chmod 600 ~/.pypirc
```

**Option 2: Using environment variables** (Recommended for CI/CD)

```bash
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=pypi-AgEIcHlwaS5vcmc...YOUR-TOKEN-HERE...
```

---

## 📦 Building the Package

### 1. Clean Previous Builds

```bash
# Remove old build artifacts
rm -rf build/ dist/ *.egg-info wikijs_python_sdk.egg-info

# Verify clean state
git status
```

### 2. Update Version

```bash
# Edit wikijs/version.py
__version__ = "0.2.0"  # Update version number
__version_info__ = (0, 2, 0)
```

### 3. Update CHANGELOG

```markdown
# Edit docs/CHANGELOG.md

## [0.2.0] - 2025-10-XX

### Added
- New feature descriptions
- API additions

### Changed
- Modified functionality

### Fixed
- Bug fixes
```

### 4. Build Distributions

```bash
# Build both source distribution (sdist) and wheel
python -m build

# This creates:
# - dist/wikijs_python_sdk-X.Y.Z.tar.gz (source distribution)
# - dist/wikijs_python_sdk-X.Y.Z-py3-none-any.whl (wheel)
```

### 5. Verify Build Contents

```bash
# Check source distribution contents
tar -tzf dist/wikijs_python_sdk-*.tar.gz | head -30

# Check wheel contents
python -m zipfile -l dist/wikijs_python_sdk-*-py3-none-any.whl | head -30

# Verify required files are included:
# - LICENSE
# - README.md
# - requirements.txt
# - docs/
# - examples/
# - wikijs/ (all source code)
# - wikijs/py.typed (type stub marker)
```

---

## 🧪 Testing the Package

### 1. Validate Package Metadata

```bash
# Check package metadata for errors
python -m twine check dist/*

# Should show:
# Checking dist/wikijs_python_sdk-X.Y.Z.tar.gz: PASSED
# Checking dist/wikijs_python_sdk-X.Y.Z-py3-none-any.whl: PASSED
```

### 2. Test Local Installation

```bash
# Create a test virtual environment
python -m venv test-env
source test-env/bin/activate  # On Windows: test-env\Scripts\activate

# Install from wheel
pip install dist/wikijs_python_sdk-*-py3-none-any.whl

# Test import
python -c "from wikijs import WikiJSClient, __version__; print(f'Version: {__version__}')"

# Test basic functionality
python << 'EOF'
from wikijs import WikiJSClient
from wikijs.models import PageCreate

# This should not error (will fail at connection, which is expected)
try:
    client = WikiJSClient('https://example.com', auth='test-key')
    print("✅ Client instantiation successful")
except Exception as e:
    print(f"❌ Error: {e}")
EOF

# Cleanup
deactivate
rm -rf test-env
```

### 3. Test on TestPyPI (Optional but Recommended)

```bash
# Upload to TestPyPI first
python -m twine upload --repository testpypi dist/*

# Install from TestPyPI
pip install --index-url https://test.pypi.org/simple/ \
    --extra-index-url https://pypi.org/simple/ \
    py-wikijs

# Test the installation
python -c "from wikijs import WikiJSClient; print('TestPyPI install successful')"
```

---

## 🚀 Publishing to PyPI

### 1. Final Pre-Publish Checks

```bash
# Ensure you're on the main branch
git checkout main

# Ensure everything is committed
git status

# Tag the release
git tag v0.2.0
git push origin v0.2.0
```

### 2. Upload to PyPI

```bash
# Upload to production PyPI
python -m twine upload dist/*

# You'll see output like:
# Uploading distributions to https://upload.pypi.org/legacy/
# Uploading wikijs_python_sdk-0.2.0-py3-none-any.whl
# Uploading wikijs_python_sdk-0.2.0.tar.gz
# View at:
# https://pypi.org/project/py-wikijs/0.2.0/
```

### 3. Verify Publication

```bash
# Visit PyPI page
# https://pypi.org/project/py-wikijs/

# Test installation from PyPI
pip install py-wikijs

# Verify version
python -c "from wikijs import __version__; print(__version__)"
```

---

## 🔄 Post-Publication Tasks

### 1. Update Documentation

- [ ] Update README.md installation instructions
- [ ] Update GitHub releases page
- [ ] Announce release in community channels
- [ ] Update project status badges

### 2. Git Housekeeping

```bash
# Create GitHub release
# Go to: https://github.com/l3ocho/py-wikijs/releases/new
# - Tag version: v0.2.0
# - Release title: v0.2.0 - Release Name
# - Description: Copy from CHANGELOG.md
# - Attach dist/ files

# Merge release branch if applicable
git checkout main
git merge release/v0.2.0
git push origin main
```

### 3. Prepare for Next Development Cycle

```bash
# Bump to next development version
# Edit wikijs/version.py
__version__ = "0.3.0-dev"

git add wikijs/version.py
git commit -m "chore: bump version to 0.3.0-dev"
git push
```

---

## 🐛 Troubleshooting

### Build Failures

**Problem**: `FileNotFoundError: requirements.txt`

```bash
# Solution: Ensure MANIFEST.in includes requirements.txt
# Check MANIFEST.in contents:
cat MANIFEST.in
```

**Problem**: Missing documentation in package

```bash
# Solution: Update MANIFEST.in to include docs
recursive-include docs *.md
```

### Upload Failures

**Problem**: `403 Forbidden - Invalid or non-existent authentication information`

```bash
# Solution: Check your API token
# 1. Verify token is correct in ~/.pypirc
# 2. Ensure token has upload permissions
# 3. Try using environment variables instead
export TWINE_USERNAME=__token__
export TWINE_PASSWORD=your-token-here
python -m twine upload dist/*
```

**Problem**: `400 File already exists`

```bash
# Solution: You cannot re-upload the same version
# 1. Increment version in wikijs/version.py
# 2. Rebuild: python -m build
# 3. Upload again: python -m twine upload dist/*
```

**Problem**: Package name already taken

```bash
# Solution: Choose a different package name
# 1. Update name in setup.py and pyproject.toml
# 2. Rebuild package
# Note: py-wikijs is our chosen name
```

### Installation Issues

**Problem**: `ModuleNotFoundError` after install

```bash
# Solution: Check dependencies are installed
pip show py-wikijs
pip install py-wikijs[all]  # Install all optional deps
```

**Problem**: Import errors with type hints

```bash
# Solution: Ensure py.typed file is in package
# Check if included: python -m zipfile -l dist/*.whl | grep py.typed
```

---

## 📊 Package Statistics

### Size Guidelines

- **Wheel**: Should be < 100 KB for SDK
- **Source**: Should be < 200 KB including docs
- **Total dependencies**: Keep minimal

```bash
# Check package sizes
ls -lh dist/

# Check dependency tree
pip install pipdeptree
pipdeptree -p py-wikijs
```

### Download Stats

After publication, monitor package metrics:

- **PyPI Stats**: https://pypistats.org/packages/py-wikijs
- **GitHub Stats**: Stars, forks, watchers
- **Issue Tracker**: Open issues, response time

---

## 🔐 Security Best Practices

### 1. Protect API Tokens

- Never commit tokens to git
- Use `.gitignore` for `.pypirc`
- Rotate tokens periodically
- Use scoped tokens (project-specific)

### 2. Package Security

```bash
# Run security scan before publishing
pip install safety
safety check --file requirements.txt

# Scan for vulnerabilities
bandit -r wikijs/
```

### 3. Signing Releases (Optional)

```bash
# Sign the release with GPG
gpg --detach-sign -a dist/wikijs_python_sdk-0.2.0.tar.gz

# Upload signatures
python -m twine upload dist/* --sign
```

---

## 📝 Checklist Summary

### Pre-Release
- [ ] Tests pass
- [ ] Version bumped
- [ ] CHANGELOG updated
- [ ] Documentation current

### Build
- [ ] Clean build environment
- [ ] Build succeeds
- [ ] Package validated
- [ ] Local test passes

### Publish
- [ ] TestPyPI upload (optional)
- [ ] PyPI upload
- [ ] Installation verified
- [ ] Package page checked

### Post-Release
- [ ] Git tag created
- [ ] GitHub release published
- [ ] Documentation updated
- [ ] Community notified

---

## 📞 Support

### Resources
- **PyPI Help**: https://pypi.org/help/
- **Packaging Guide**: https://packaging.python.org/
- **Twine Docs**: https://twine.readthedocs.io/

### Getting Help
- PyPI Support: https://pypi.org/help/#feedback
- GitHub Issues: https://github.com/l3ocho/py-wikijs/issues
- Packaging Discourse: https://discuss.python.org/c/packaging/

---

## 🎓 Additional Notes

### Automated Publishing (CI/CD)

For automated releases via GitHub Actions:

```yaml
# .github/workflows/publish.yml
name: Publish to PyPI

on:
  release:
    types: [published]

jobs:
  pypi-publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.10'
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

### Alternative: Using Trusted Publishing

Modern approach (no API tokens needed):

1. Configure trusted publisher on PyPI
2. Use OIDC token from GitHub Actions
3. More secure, no secrets needed

See: https://docs.pypi.org/trusted-publishers/

---

**Last Updated**: October 2025
**Maintainer**: leomiranda

For questions about deployment, open an issue on GitHub.
