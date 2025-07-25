"""Cloud Function for processing LFP (Local Field Potential) neural data streams."""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_processor import process_neural_stream  # noqa: E402, F401

# LFP uses the base processor with its specific configuration
