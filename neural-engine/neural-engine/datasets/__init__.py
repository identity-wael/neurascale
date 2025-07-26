"""Dataset management for neural data processing.

This module provides infrastructure for loading, managing, and preprocessing
various types of neural datasets including BCI competition data, PhysioNet
datasets, and custom formats.
"""

from .base_dataset import BaseDataset, DatasetInfo, DatasetSplit, DataSample
from .dataset_manager import DatasetManager, DatasetRegistry
from .synthetic_dataset import SyntheticNeuralDataset

__all__ = [
    "BaseDataset",
    "DatasetInfo",
    "DatasetSplit",
    "DataSample",
    "DatasetManager",
    "DatasetRegistry",
    "SyntheticNeuralDataset",
]

__version__ = "0.1.0"
