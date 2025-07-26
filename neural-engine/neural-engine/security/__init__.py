"""NeuraScale Security Module.

This module provides encryption, authentication, and security features
for protecting sensitive neural data in compliance with HIPAA and other
healthcare regulations.
"""

from .encryption import (
    NeuralDataEncryption,
    FieldLevelEncryption,
    EncryptionError,
    KeyRotationError,
)

__all__ = [
    "NeuralDataEncryption",
    "FieldLevelEncryption",
    "EncryptionError",
    "KeyRotationError",
]
