#!/usr/bin/env python3
"""
Setup script for Multi-Agent System Backend
"""

from setuptools import setup, find_packages
import os

# Read the README file
def read_readme():
    readme_path = os.path.join(os.path.dirname(__file__), 'README.md')
    if os.path.exists(readme_path):
        with open(readme_path, 'r', encoding='utf-8') as f:
            return f.read()
    return "Multi-Agent System Backend for business compliance and validation"

# Read requirements
def read_requirements():
    requirements_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')
    if os.path.exists(requirements_path):
        with open(requirements_path, 'r', encoding='utf-8') as f:
            return [line.strip() for line in f if line.strip() and not line.startswith('#')]
    return []

setup(
    name="multi-agent-backend",
    version="1.0.0",
    description="AI-powered backend system for business compliance and validation operations",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    author="Multi-Agent System Team",
    author_email="team@example.com",
    url="https://github.com/your-org/multi-agent-system",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    extras_require={
        "dev": [
            "pytest>=8.2.2",
            "pytest-asyncio>=0.24.0",
            "pytest-cov>=5.0.0",
            "black>=24.10.0",
            "flake8>=7.0.0",
            "mypy>=1.13.0",
            "isort>=5.13.2",
        ],
        "docs": [
            "sphinx>=8.2.2",
            "sphinx-rtd-theme>=2.0.0",
        ],
        "full": [
            "fastapi>=0.115.6",
            "uvicorn>=0.32.1",
            "sqlalchemy>=2.0.36",
            "redis>=5.2.1",
            "celery>=5.4.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "multi-agent-backend=main:main",
            "vat-validator=agents.vat_validation_agent:validate_vat_cli",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
    keywords=[
        "ai", "agents", "vat", "validation", "compliance", "business",
        "langchain", "ollama", "scraping", "belgium", "europe"
    ],
    project_urls={
        "Bug Reports": "https://github.com/your-org/multi-agent-system/issues",
        "Source": "https://github.com/your-org/multi-agent-system",
        "Documentation": "https://github.com/your-org/multi-agent-system/docs",
    },
) 