#!/usr/bin/env python3
"""Setup script for Wiki.js Python SDK."""

from setuptools import setup, find_packages
import os


def read_version():
    """Read version from wikijs/version.py."""
    version_file = os.path.join("wikijs", "version.py")
    with open(version_file, "r", encoding="utf-8") as f:
        for line in f:
            if line.startswith("__version__"):
                return line.split("=")[1].strip().strip('"').strip("'")
    raise RuntimeError("Unable to find version string.")


def read_readme():
    """Read README.md for long description."""
    with open("README.md", "r", encoding="utf-8") as f:
        return f.read()


def read_requirements():
    """Read requirements.txt for dependencies."""
    with open("requirements.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]


def read_dev_requirements():
    """Read requirements-dev.txt for development dependencies."""
    try:
        with open("requirements-dev.txt", "r", encoding="utf-8") as f:
            deps = []
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and not line.startswith("-r"):
                    deps.append(line)
            return deps
    except FileNotFoundError:
        return []


setup(
    name="py-wikijs",
    version=read_version(),
    description="A professional Python SDK for Wiki.js API integration",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="leomiranda",
    author_email="lmiranda@hotserv.cloud",
    url="https://github.com/l3ocho/py-wikijs",
    project_urls={
        "Bug Reports": "https://github.com/l3ocho/py-wikijs/issues",
        "Source": "https://github.com/l3ocho/py-wikijs",
        "Documentation": "https://github.com/l3ocho/py-wikijs/blob/main/docs",
        "Compatibility": "https://github.com/l3ocho/py-wikijs/blob/main/docs/compatibility.md",
        "Wiki.js": "https://js.wiki",
    },
    packages=find_packages(),
    include_package_data=True,
    package_data={
        "wikijs": ["py.typed"],
    },
    install_requires=read_requirements(),
    extras_require={
        "dev": read_dev_requirements(),
        "async": ["aiohttp>=3.8.0"],
        "cli": ["click>=8.0.0", "rich>=12.0.0"],
        "all": ["aiohttp>=3.8.0", "click>=8.0.0", "rich>=12.0.0"],
    },
    python_requires=">=3.8",
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
    keywords=["wiki", "wikijs", "wiki.js", "api", "sdk", "client", "http", "rest", "graphql", "wiki.js-2.x"],
    zip_safe=False,
)