"""Test runner to verify all device tests."""

import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, project_root)

def test_imports():
    """Test that all test modules can be imported."""
    try:
        from . import test_base_device
        print("✓ test_base_device imported successfully")

        from . import test_signal_quality
        print("✓ test_signal_quality imported successfully")

        from . import test_device_discovery
        print("✓ test_device_discovery imported successfully")

        from . import test_brainflow_device
        print("✓ test_brainflow_device imported successfully")

        from . import test_device_manager
        print("✓ test_device_manager imported successfully")

        print("\nAll test modules imported successfully!")
        return True

    except ImportError as e:
        print(f"✗ Import error: {e}")
        return False


if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
