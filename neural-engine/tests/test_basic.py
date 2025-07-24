"""Basic tests to verify the Neural Engine setup."""

import pytest


def test_environment_setup():
    """Test that the basic environment is set up correctly."""
    assert True


def test_python_version():
    """Test Python version is compatible."""
    import sys
    assert sys.version_info >= (3, 11)
    assert sys.version_info < (3, 13)


def test_imports():
    """Test that core dependencies can be imported."""
    # Test neural signal processing imports
    try:
        import pylsl
        has_lsl = True
    except RuntimeError as e:
        if "LSL binary library file was not found" in str(e):
            pytest.skip("LSL binary not available in CI environment")
        else:
            raise

    import brainflow
    import numpy
    import scipy
    import sklearn

    # Test Google Cloud imports
    from google.cloud import pubsub_v1
    from google.cloud import firestore
    from google.cloud import bigquery
    from google.cloud import storage

    # Test TensorFlow
    import tensorflow as tf

    # Basic assertions
    if has_lsl:
        assert pylsl.__version__
    assert numpy.__version__
    assert tf.__version__


@pytest.mark.asyncio
async def test_async_support():
    """Test that async/await is working."""
    async def sample_async_function():
        return "async works"

    result = await sample_async_function()
    assert result == "async works"


class TestNeuralEngineSetup:
    """Test class for Neural Engine setup verification."""

    def test_class_based_test(self):
        """Test that class-based tests work."""
        assert 1 + 1 == 2

    def test_numpy_operations(self):
        """Test basic numpy operations."""
        import numpy as np

        arr = np.array([1, 2, 3, 4, 5])
        assert arr.mean() == 3.0
        assert arr.sum() == 15

    def test_tensorflow_basics(self):
        """Test TensorFlow basic operations."""
        import tensorflow as tf

        # Create a simple tensor
        tensor = tf.constant([1, 2, 3, 4])
        assert tensor.shape == (4,)
        assert tf.reduce_sum(tensor).numpy() == 10
