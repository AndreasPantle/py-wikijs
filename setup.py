"""Setup configuration for wikijs-python-sdk."""

import os
from setuptools import setup, find_packages

# Read version from file
def get_version():
    version_file = os.path.join(os.path.dirname(__file__), "wikijs", "version.py")
    if os.path.exists(version_file):
        with open(version_file) as f:
            for line in f:
                if line.startswith("__version__"):
                    return line.split("=")[1].strip().strip('"').strip("'")
    return "0.1.0"  # Fallback version

# Read long description from README
def get_long_description():
    readme_path = os.path.join(os.path.dirname(__file__), "README.md")
    if os.path.exists(readme_path):
        with open(readme_path, "r", encoding="utf-8") as fh:
            return fh.read()
    return "A professional Python SDK for Wiki.js API integration"

# Read requirements
def get_requirements():
    req_path = os.path.join(os.path.dirname(__file__), "requirements.txt")
    if os.path.exists(req_path):
        with open(req_path) as f:
            return [
                line.strip() 
                for line in f 
                if line.strip() and not line.startswith("#")
            ]
    return ["requests>=2.28.0", "pydantic>=1.10.0"]

setup(
    name="wikijs-python-sdk",
    version=get_version(),
    author="Wiki.js SDK Contributors",
    author_email="contact@wikijs-sdk.dev",
    description="A professional Python SDK for Wiki.js API integration",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/wikijs-python-sdk",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/wikijs-python-sdk/issues",
        "Source": "https://github.com/yourusername/wikijs-python-sdk",
        "Documentation": "https://github.com/yourusername/wikijs-python-sdk/docs",
    },
    packages=find_packages(exclude=["tests*", "docs*", "examples*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Documentation",
        "Typing :: Typed",
    ],
    python_requires=">=3.8",
    install_requires=get_requirements(),
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "isort>=5.10.0",
            "flake8>=5.0.0",
            "mypy>=0.991",
            "pre-commit>=2.20.0",
            "bandit[toml]>=1.7.0",
            "responses>=0.20.0",
        ],
        "async": [
            "aiohttp>=3.8.0",
        ],
        "cli": [
            "click>=8.0.0",
            "rich>=12.0.0",
        ],
        "all": [
            "aiohttp>=3.8.0",
            "click>=8.0.0", 
            "rich>=12.0.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "wikijs=wikijs.cli.main:main [cli]",
        ],
    },
    include_package_data=True,
    package_data={
        "wikijs": ["py.typed"],
    },
    keywords="wiki wikijs api sdk client http rest",
    zip_safe=False,
)