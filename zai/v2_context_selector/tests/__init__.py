"""
Test suite for the V2 Context Selection System.
"""

import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from v2_context_selector.core.models import TextSegment
from v2_context_selector.core.selector import ContextSelector
from v2_context_selector.config.settings import Config, fast_config, balanced_config, accurate_config

__all__ = [
    "TextSegment",
    "ContextSelector",
    "Config",
    "fast_config",
    "balanced_config",
    "accurate_config"
]