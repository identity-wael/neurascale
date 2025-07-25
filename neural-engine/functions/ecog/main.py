"""Cloud Function for processing ECoG neural data streams."""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from base_processor import process_neural_stream

# ECoG uses the base processor with its specific configuration
# The base processor already handles ECoG-specific settings
