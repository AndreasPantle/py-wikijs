# Security Policy

## Supported Versions

| Version | Supported          |
| ------- | ------------------ |
| 0.3.x   | :white_check_mark: |
| 0.2.x   | :white_check_mark: |
| 0.1.x   | :x:                |

## Reporting a Vulnerability

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, please report them via email to: **lmiranda@hotserv.cloud**

Include the following information:
- Type of vulnerability
- Full paths of affected source files
- Location of affected source code (tag/branch/commit)
- Step-by-step instructions to reproduce
- Proof-of-concept or exploit code (if possible)
- Impact of the issue

### Response Timeline

- **Initial Response**: Within 48 hours
- **Status Update**: Within 7 days
- **Fix Timeline**: Depends on severity
  - Critical: 7-14 days
  - High: 14-30 days
  - Medium: 30-60 days
  - Low: Best effort

## Security Best Practices

### API Keys
- Never commit API keys to version control
- Use environment variables for sensitive data
- Rotate API keys regularly
- Use separate keys for different environments

### SSL/TLS
- Always use HTTPS for Wiki.js instances
- Verify SSL certificates (verify_ssl=True)
- Use modern TLS versions (1.2+)
- Keep certificates up to date

### Dependencies
- Keep dependencies updated
- Monitor security advisories
- Use pip-audit for vulnerability scanning
- Review dependency changes before upgrading

### Authentication
- Use JWT authentication for production
- Implement token refresh mechanisms
- Store tokens securely
- Never log authentication credentials

### Input Validation
- Always validate user input
- Use type hints and Pydantic models
- Sanitize data before processing
- Check for injection vulnerabilities

## Disclosure Policy

Once a vulnerability is fixed:
1. We will publish a security advisory
2. Credit will be given to the reporter (if desired)
3. Details will be disclosed responsibly
4. Users will be notified through appropriate channels

## Security Features

### Built-in Security
- Request validation using Pydantic
- SSL certificate verification by default
- Rate limiting to prevent abuse
- Structured logging for audit trails
- No hardcoded credentials

### Recommended Practices
```python
# Good: Use environment variables
import os
from wikijs import WikiJSClient

client = WikiJSClient(
    os.getenv("WIKIJS_URL"),
    auth=os.getenv("WIKIJS_API_KEY"),
    verify_ssl=True
)

# Bad: Hardcoded credentials
# client = WikiJSClient(
#     "https://wiki.example.com",
#     auth="my-secret-key"  # DON'T DO THIS
# )
```

## Contact

For security concerns, contact:
- **Email**: lmiranda@hotserv.cloud
- **Repository**: https://gitea.hotserv.cloud/lmiranda/py-wikijs

## Acknowledgments

We appreciate the security researchers and contributors who help make this project more secure.
