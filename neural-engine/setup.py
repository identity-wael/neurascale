"""Setup configuration for NeuraScale Neural Engine."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="neurascale-neural-engine",
    version="0.1.0",
    author="NeuraScale",
    author_email="dev@neurascale.io",
    description="Neural Engine for real-time brain signal processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/identity-wael/neurascale",
    packages=find_packages(exclude=["tests", "tests.*"]),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.11,<3.14",
    install_requires=[
        "pylsl>=1.16.0",
        "brainflow>=5.10.0",
        "numpy>=1.24.3",
        "scipy>=1.10.1",
        "scikit-learn>=1.3.0",
        "tensorflow>=2.13.0",
        "google-cloud-pubsub>=2.18.1",
        "google-cloud-firestore>=2.11.1",
        "google-cloud-bigquery>=3.11.4",
        "google-cloud-bigtable>=2.19.0",
        "google-cloud-storage>=2.10.0",
        "flask>=2.3.3",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.1",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.1.0",
            "mypy>=1.5.1",
        ],
    },
    entry_points={
        "console_scripts": [
            "neural-engine=neural_engine.cli:main",
        ],
    },
)
