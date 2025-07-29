"""Setup script for NeuraScale Python SDK."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="neurascale",
    version="2.0.0",
    author="NeuraScale",
    author_email="support@neurascale.com",
    description="Python SDK for NeuraScale Neural Engine API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/neurascale/python-sdk",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Medical Science Apps.",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "httpx>=0.25.0",
        "pydantic>=2.0.0",
        "python-dateutil>=2.8.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "ruff>=0.1.0",
        ],
        "docs": [
            "sphinx>=6.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ],
    },
)
