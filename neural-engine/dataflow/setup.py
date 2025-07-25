"""Setup file for Dataflow pipeline dependencies."""

import setuptools

REQUIRED_PACKAGES = [
    'apache - beam[gcp]>=2.50.0',
    'numpy>=1.24.0',
    'scipy>=1.10.0',
]

setuptools.setup(
    name='neural - processing - pipeline',
    version='0.1.0',
    description='Neural data processing pipeline for NeuraScale',
    install_requires=REQUIRED_PACKAGES,
    packages=setuptools.find_packages(),
)
